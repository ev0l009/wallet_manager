# 6\. Persistence Architecture and Integrity Guard

## 6.1 Serialization Lifecycle (`json.dump` / `json.load`)

### Data Extraction (Deserialization)

- Upon application startup, `file_manager/` (`load_app_data()`) first removes any stale `.storage.json.tmp` file (logging a warning) and checks whether `.storage.json` exists:
  - **Missing file (first run):** Returns a clean empty `WalletEngineData` state without failing.
  - **Existing file:** Reads the file using Python's native `json.load()` into native Python dictionaries and lists.
- `file_manager/` validates the top-level JSON structure (confirming expected root keys and list containers for `accounts` and `transactions`).
- Valid records are reconstructed into domain entities by delegating to `Account.from_dict()` and `Transaction.from_dict()` in `models/`, while indexing `accounts` into `WalletEngineData["accounts"]` (`dict[str, Account]`).
- Integer monetary values (minor units) must remain Python `int` values after deserialization (rejecting floats or booleans).
- Malformed JSON, OS read errors, invalid root structure, duplicate account IDs encountered while building the `accounts` dictionary, or invalid single-record fields detected by `from_dict()` (such as invalid account statuses, transaction classifications, identifiers, or monetary values) raise **`StorageReadError`** and halt startup so the app never falls back to an empty state.
- Cross-entity reference checks (duplicate transaction IDs detected via a seen-IDs set, valid `source_acc_id`, `target_acc_id`, and `reverses_transaction_id` links, and no double-reversals) are executed in `services/` (`_validate_loaded_data()`), followed by `_validate_chronological_balances()`, which runs `validate_account_timeline()` across every loaded account—raising **`StorageReadError`** and halting startup if any violation is found.

### Data Serialization

- When application state changes, `file_manager/` converts domain entities via `Account.to_dict()` and `Transaction.to_dict()` and serializes the complete proposed state using Python's native `json.dump()` method.
- Both `accounts` and `transactions` are serialized as JSON lists so entity IDs are stored once inside each object without duplicate dictionary keys.
- JSON serialization uses a consistent indentation format (`indent=2`) to preserve human readability at our v1 personal-scale advisory target of **up to ~5,000 transactions** (~1–2 MB); exceeding this target or seeing noticeable save latency triggers migrating `file_manager/` to SQLite.
- Monetary values must be serialized as JSON integers (minor units) rather than floating-point numbers.
- Historical transactions are never modified and retain their original identifiers and immutable attributes on every serialization pass.


## 6.2 Atomic Write Fail-Safe Strategy

- The application must never write directly into the active JSON storage file during normal state updates.
- Instead, the complete proposed application state must first be written into a temporary staging file named `.storage.json.tmp`.
- The staging file must be created in the same directory as the destination `storage.json` file.
- After the staging file has been completely written and flushed, the Data Access Layer must execute `os.replace()` to atomically replace the active storage file.
- The replacement operation must occur only after successful serialization and staging-file writing.

**Atomic replacement guarantees:**

- Both files reside on the same filesystem.
- Readers will observe either the previous complete JSON file or the newly replaced JSON file, subject to the supported filesystem's atomic replacement guarantees.
- The destination file will not be exposed as a partially serialized JSON document during a successful atomic replacement.

**Durability limitation:**

Atomic replacement alone does not guarantee complete durability against every possible operating-system crash or power failure. Stronger crash-durability guarantees would require additional filesystem synchronization measures, including appropriate use of `fsync()`.

## 6.3 In-Memory State Consistency and Transaction Commit

- The system must never mutate the active in-memory application state before successfully persisting the corresponding changes to disk.
- Before executing any state-changing operation (creating, renaming, deactivating, or reactivating an account, or recording a new transaction or reversal), `services/` creates a shallow copy of the `WalletEngineData` containers (`dict(accounts)` and `list(transactions)`) as an independent proposed state.
- Proposed changes are applied exclusively to this proposed state: new transactions are appended to the proposed list, and modified `Account` entities (such as on rename, deactivation, or reactivation) are **replaced with new `Account` instances** in the proposed dictionary rather than mutated in place (account balances remain derived from the ledger rather than stored on `Account`).
- `file_manager/` serializes and persists the complete proposed state using the staging-file (`.storage.json.tmp` with `flush()` + `os.fsync()`) and atomic replacement (`os.replace()`) strategy.
- Only after successful completion of the file replacement operation may `services/` commit the proposed `WalletEngineData` as the new active in-memory application state.
- If persistence fails at any stage:
  - The proposed state is discarded.
  - The original in-memory containers and existing `Account` instances remain completely unchanged.
  - The previously persisted `.storage.json` file remains unchanged where failure occurs before successful replacement.
  - A `StorageWriteError` is raised.
  - `ui/` catches `StorageWriteError` and reports the failure without displaying a success confirmation.

This process ensures that the application never exposes an unpersisted state change or financial transaction as a successful operation.


## 6.4 Transaction Guarantee and Failure Boundaries

The application implements a single-file transactional persistence strategy rather than a full database transaction mechanism.

The logical transaction consists of proposed account state updates and append-only ledger additions (including `INCOME`, `EXPENSE`, `TRANSFER`, and `REVERSAL` entries), persisted together through one complete JSON state replacement.

**The system guarantees that:**

- The active in-memory application state remains unchanged until successful file replacement.
- The existing `.storage.json` file remains intact if serialization, staging-file writing, or `fsync` fails before `os.replace()`.
- A successful replacement makes the complete new JSON state visible as the active persisted state.
- A failed replacement prevents the proposed in-memory state from being committed.
- Account status/metadata changes and transaction ledger additions are committed together in one atomic file replacement.
- Transfer reversals affecting two accounts are persisted atomically as a single offsetting `REVERSAL` transaction (with flipped `source_acc_id` and `target_acc_id`) within one complete state update.

**The system does not guarantee:**

- Database-level transaction isolation.
- Multi-process concurrency control.
- Protection against every possible hardware failure.
- Guaranteed recovery from every operating-system crash.
- Automatic rollback after an atomic file replacement has already succeeded.

These capabilities are outside the current single-process JSON persistence architecture (capped at 5,000 transactions).


## 6.5 Persistence Scalability Constraints

- The application will use one structured JSON file as its exclusive persistence mechanism.
- The system is designed for a single-user, single-process environment with moderate transaction volumes.
- The accepted operational capacity for the current release is up to **5,000 historical transaction records**.
- Transaction retrieval, compound filtering, sorting, and pagination will be performed in application memory after loading the JSON dataset.
- Pagination will limit the number of records returned to the presentation layer but will not eliminate the computational cost of loading and processing the underlying transaction collection.
- The application must monitor the number of historical transaction records stored in the JSON ledger.

**Capacity warning:**

- When the transaction count reaches 4,000 records, the system must display a capacity warning informing the user that the application is approaching its supported transaction limit.

**Maximum capacity enforcement:**

- The application must enforce a maximum capacity of 10,000 historical transaction records.
- Once the ledger reaches 5,000 records, the system must reject any new INCOME, EXPENSE, TRANSFER, or REVERSAL operation that would increase the count beyond the supported limit.
- Capacity validation must occur before proposed account balance mutations, ledger modifications, or persistence operations.
- Existing in-memory and persisted states must remain unchanged following capacity rejection.
- The user must receive a clear notification explaining that transaction capacity has been reached and that a persistence architecture reassessment is required.

**Future migration path:**

- Transaction volumes exceeding the supported capacity will require an explicit architecture reassessment.
- SQLite is identified as the preferred migration path because it provides structured queries, indexing, and transactional capabilities.

---