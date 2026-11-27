# **6. Persistence Architecture and Integrity Guard**

## **6.1 Serialization Lifecycle (**`json.dump`**&#x20;/&#x20;**`json.load`**)**

### **Data Extraction (Deserialization)**

- Upon application startup, `file_manager/` (`load_app_data()`) checks for and removes any stale `.storage.json.tmp` file, logging a warning when one is found.
- A stale temporary file is never treated as committed application data. The active `storage.json` file remains the authoritative persistence source.
- If stale temporary-file removal fails, startup must fail with a `StorageReadError` rather than silently continue with an unresolved storage condition.
- The application then checks whether `storage.json` exists:
  - **Missing file (first run):** Returns a clean, empty `WalletEngineData` state without failing.
  - **Existing file:** Reads the file using Python's native `json.load()` into native Python dictionaries and lists.
- The Data Access Layer validates the top-level JSON structure, confirming the presence and expected types of the `accounts` and `transactions` containers.
- The persisted JSON structure must contain:
  - An account dictionary keyed by account identifiers.
  - A transaction list containing transaction records.
- Duplicate JSON object keys must be detected during parsing rather than silently overwritten by Python's default JSON parser.
- Account records are reconstructed into domain entities by delegating to `Account.from_dict()` and indexed into `WalletEngineData["accounts"]` (`dict[str, Account]`), using account identifiers as dictionary keys.
- Each account record's identifier must match the dictionary key under which it is stored.
- Transaction records are reconstructed into domain entities by delegating to `Transaction.from_dict()` and stored in `WalletEngineData["transactions"]` (`list[Transaction]`).
- Integer monetary values (minor units) must remain Python `int` values after deserialization. Floating-point values and booleans must be rejected as monetary values.
- Account records must not contain stored or cached balance attributes.
- Malformed JSON, OS read errors, invalid root structures, duplicate JSON object keys, mismatched account identifiers, or invalid individual record fields detected by `from_dict()` must prevent application startup.
- Filesystem and JSON syntax failures must raise `StorageReadError`.
- Invalid root structures, duplicate JSON object keys, invalid entity fields, mismatched identifiers, and other structural integrity violations must raise `DataIntegrityError`.
- Cross-entity reference checks are executed in `services/` through `_validate_loaded_data()`.
- These checks must include:
  - Duplicate transaction IDs, detected using a set of previously encountered transaction identifiers.
  - Valid `source_acc_id` and `target_acc_id` references where applicable to the transaction classification.
  - Valid account references for every transaction.
  - Valid transaction classifications and category combinations.
  - Compliance with historical reference constraints.
- Historical account references must be validated by checking that the referenced account identifiers exist in the loaded account collection.
- Historical transactions must not be rejected solely because their financial dates precede the referenced accounts' creation timestamps.
- Historical transactions associated with currently inactive accounts must remain valid. Current account status must not invalidate otherwise valid historical account references.
- Account activity requirements apply when entering new transactions. They must not be used to retroactively invalidate historical transactions.
- Following successful structural and cross-entity validation, `_validate_chronological_balances()` must validate the historical financial integrity of every loaded account, including inactive accounts.
- Chronological validation must consider all historical transactions regardless of account creation timestamps.
- Any account whose historical running balance becomes negative must cause startup validation to fail.
- A chronological balance violation must raise `NegativeBalanceError` (a `DataIntegrityError` subclass carrying the affected account ID, transaction date, and calculated balance).
- All integrity violations must halt startup rather than silently replacing invalid persisted data with an empty application state.

### **Data Serialization**

- When application state changes, `file_manager/` converts domain entities through `Account.to_dict()` and `Transaction.to_dict()`.
- The complete proposed application state must be serialized using Python's native `json.dump()` method.
- Accounts must be serialized as a JSON object keyed by their unique account identifiers.
- Transactions must be serialized as a JSON list.
- Each account identifier must appear once within its account record and must correspond to the dictionary key under which that record is stored.
- JSON serialization must use a consistent indentation format (`indent=2`) to preserve human readability.
- The application targets approximately 5,000 historical transaction records for its intended personal-scale operational workload.
- Exceeding this target or experiencing noticeable serialization and retrieval latency must trigger an architecture reassessment.
- Monetary values must be serialized as JSON integers (Kobo) rather than floating-point numbers.
- Account records must not contain balance fields.
- Historical transactions must never be modified and must retain their original identifiers and immutable attributes during subsequent serialization operations.

## **6.2 Atomic Write Fail-Safe Strategy**

- The application must never write directly into the active JSON storage file during normal state updates.
- Instead, the complete proposed application state must first be written into a temporary staging file named `.storage.json.tmp`.
- The staging file must be created in the same directory as the destination `storage.json` file.
- After the staging file has been completely written and flushed, the Data Access Layer must execute `os.replace()` to atomically replace the active storage file.
- The staging-file write process must use `flush()` and `os.fsync()` before replacement.
- The replacement operation must occur only after successful serialization and staging-file writing.
- The temporary staging file must be closed before the replacement operation.

**Atomic replacement guarantees:**

- Both files reside on the same filesystem.
- Readers will observe either the previous complete JSON file or the newly replaced JSON file, subject to the supported filesystem's atomic replacement guarantees.
- The destination file will not be exposed as a partially serialized JSON document during a successful atomic replacement.
- A failed staging-file write or replacement operation must not result in the proposed application state being committed to active memory.
- The successful `os.replace()` operation represents the persistence commit point.

**Durability limitation:**

Atomic replacement alone does not guarantee complete durability against every possible operating-system crash or power failure.

Stronger crash-durability guarantees would require additional filesystem synchronization measures, including appropriate directory synchronization after replacement.

## **6.3 In-Memory State Consistency and Transaction Commit**

- The system must never mutate the active in-memory application state before successfully persisting the corresponding changes to disk.
- Before executing any state-changing operation (creating, renaming, deactivating, or reactivating an account, or recording a new INCOME, EXPENSE, or TRANSFER transaction), `services/` must create a proposed application state.
- The proposed state must contain independent copies of the `WalletEngineData` containers:
  - `dict(accounts)`
  - `list(transactions)`
- Existing domain entities must not be mutated in place while preparing proposed state.
- Proposed changes must be applied exclusively to the proposed state.
- New transactions must be appended to the proposed transaction list.
- Modified Account entities, such as renamed, deactivated, or reactivated accounts, must be replaced with new Account instances in the proposed account dictionary rather than mutated in place.
- Existing transaction instances must remain unchanged. The transaction list is append-only.
- Account balances must not be updated or stored because they are derived dynamically from the transaction ledger.
- Counteracting transactions must be handled as ordinary new transactions and appended to the proposed transaction list using their appropriate classifications.
- All applicable business validations, including chronological balance validation, must be completed against the proposed state before persistence.
- `file_manager/` must serialize and persist the complete proposed state using the staging-file (`.storage.json.tmp` with `flush()` and `os.fsync()`) and atomic replacement (`os.replace()`) strategy.
- Only after successful completion of the file replacement operation may `services/` commit the proposed `WalletEngineData` as the new active in-memory application state.

If persistence fails at any stage before successful replacement:

- The proposed state must be discarded.
- The original in-memory containers and existing Account instances must remain unchanged.
- The previously persisted `storage.json` file must remain unchanged.
- A `StorageWriteError` must be raised.
- `ui/` must catch `StorageWriteError` and report the failure without displaying a success confirmation.

If replacement succeeds, the proposed state is considered persisted and must subsequently become the active in-memory state. The application does not guarantee rollback if a failure occurs after successful replacement.

This process ensures that the application never exposes an unpersisted state change or financial transaction as a successfully completed operation.

## **6.4 Transaction Guarantee and Failure Boundaries**

The application implements a single-file transactional persistence strategy rather than a full database transaction mechanism.

The logical transaction consists of proposed account metadata changes and append-only ledger additions, including INCOME, EXPENSE, and TRANSFER transactions, persisted together through one complete JSON state replacement.

**The system guarantees that:**

- The active in-memory application state remains unchanged until successful file replacement.
- The existing `storage.json` file remains intact if serialization, staging-file writing, or `fsync()` fails before `os.replace()`.
- A successful replacement makes the complete new JSON state visible as the active persisted state, subject to the supported filesystem's atomic replacement guarantees.
- A failed replacement prevents the proposed in-memory state from being committed.
- Account creation, renaming, activation/deactivation, and transaction ledger additions are committed together through one atomic file replacement.
- Internal transfers affecting two accounts are persisted as one ordinary TRANSFER transaction within a single complete state update.
- Counteracting transactions are persisted as ordinary transactions within the same atomic persistence mechanism.
- Account balances are always derived from the resulting transaction ledger rather than independently mutated or persisted.

**The system does not guarantee:**

- Database-level transaction isolation.
- Multi-process concurrency control.
- Protection against every possible hardware failure.
- Guaranteed recovery from every operating-system crash.
- Automatic rollback after an atomic file replacement has already succeeded.

These capabilities are outside the current single-process JSON persistence architecture.

## **6.5 Persistence Scalability Constraints**

- The application will use one structured JSON file as its exclusive persistence mechanism.
- The system is designed for a single-user, single-process environment with moderate transaction volumes.
- The intended operational workload for the current release is approximately 5,000 historical transaction records.
- The application will enforce an absolute maximum capacity of 10,000 historical transaction records.
- The transaction warning threshold and maximum record capacity must be maintained as centralized constants in `utils/constants.py`.
- Transaction retrieval, compound filtering, sorting, and pagination will be performed in application memory after loading the JSON dataset.
- Pagination will limit the number of records returned to the presentation layer but will not eliminate the computational cost of loading and processing the underlying transaction collection.
- The application must monitor the number of historical transaction records stored in the JSON ledger.

**Capacity warning:**

- When the transaction count reaches 4,000 records, the system must display a capacity warning informing the user that the application is approaching its intended operational capacity.
- If the application starts with 4,000 or more records, the capacity warning must also be displayed.
- The warning must communicate that the current JSON persistence architecture may require reassessment as the transaction history grows.

**Operational capacity threshold:**

- The 5,000-record threshold represents the intended operational capacity rather than an absolute transaction restriction.
- Reaching this threshold must trigger an architecture reassessment.
- The application may continue accepting valid transactions beyond this threshold, provided the absolute maximum capacity has not been reached.
- Existing transaction history must remain accessible beyond the intended operational capacity.

**Maximum capacity enforcement:**

- The application must enforce an absolute maximum capacity of 10,000 historical transaction records.
- Once the ledger contains 10,000 records, the system must reject any new INCOME, EXPENSE, or TRANSFER operation that would increase the count beyond the supported maximum.
- Capacity validation must occur before proposed application state mutations, ledger modifications, or persistence operations.
- Existing in-memory and persisted states must remain unchanged following capacity rejection.
- The user must receive a clear notification explaining that transaction capacity has been reached and that a persistence architecture reassessment is required.
- Account creation, renaming, deactivation, and reactivation must not be restricted by transaction capacity because these operations do not increase the historical transaction count.

**Future Architecture Reassessment:**

- Transaction volumes approaching or exceeding the intended operational capacity will require an explicit architecture reassessment.
- Any proposed change to the persistence mechanism must be treated as a separate architectural decision and must not introduce interchangeable storage backends into the current design.
- The current release remains exclusively dependent on the concrete JSON Data Access Layer.
- Any future architectural change must preserve historical transaction records, account identifiers, account references, and monetary precision.

---