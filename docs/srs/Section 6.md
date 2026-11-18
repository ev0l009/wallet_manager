# 6\. Persistence Architecture and Integrity Guard

## 6.1 Serialization Lifecycle (`json.dump` / `json.load`)

### Data Extraction (Deserialization)

- Upon application startup, the Data Access Layer must use Python's native `json.load()` function to read the local storage file.
- The raw JSON payload must be parsed into native Python dictionaries and lists.
- The loaded data must be validated against the expected storage structure before being exposed to the Business Logic Layer.
- Valid records must be reconstructed into their corresponding domain entities or controlled application data structures.
- Integer monetary values must remain integers after deserialization.
- Invalid persisted account statuses, transaction classifications, identifiers, monetary values, or transaction references must trigger controlled data-integrity failures.

### Data Serialization

- When application state changes, the Data Access Layer must serialize the complete proposed state using Python's native `json.dump()` method.
- JSON serialization must use a consistent indentation format to preserve human readability.
- Monetary values must be serialized as JSON integers rather than floating-point numbers.
- Historical transactions must retain their original identifiers and immutable attributes during serialization.

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
- Before executing a financial transaction, the Business Logic Layer must create an independent proposed copy of the current application state.
- Proposed account balance mutations and transaction ledger additions must be applied exclusively to this proposed state.
- The Data Access Layer must serialize and persist the complete proposed state using the staging-file and atomic replacement strategy.
- Only after successful completion of the file replacement operation may the Business Logic Layer commit the proposed state as the new active in-memory application state.
- If persistence fails at any stage:
  - The proposed state must be discarded.
  - The original in-memory state must remain unchanged.
  - The previously persisted JSON state must remain unchanged where failure occurs before successful replacement.
  - A `DatabaseWriteException` must be raised.
  - The UI must report the failure without displaying a transaction success confirmation.

This process ensures that the application does not expose an unpersisted financial transaction as a successful operation.

## 6.4 Transaction Guarantee and Failure Boundaries

The application implements a single-file transactional persistence strategy rather than a full database transaction mechanism.

The logical transaction consists of proposed account balance mutations and corresponding ledger additions, persisted together through one complete JSON state replacement.

**The system guarantees that:**

- The active in-memory application state remains unchanged until successful file replacement.
- The existing JSON file remains intact if serialization or staging-file writing fails before replacement.
- A successful replacement makes the complete new JSON state visible as the active persisted state.
- A failed replacement prevents the proposed in-memory state from being committed.
- Account balance mutations and transaction ledger additions are committed together.
- Transfer reversals affecting two accounts are persisted as one complete state update.

**The system does not guarantee:**

- Database-level transaction isolation.
- Multi-process concurrency control.
- Protection against every possible hardware failure.
- Guaranteed recovery from every operating-system crash.
- Automatic rollback after a replacement that has already succeeded.

These capabilities are outside the current single-process JSON persistence architecture.

## 6.5 Persistence Scalability Constraints

- The application will use one structured JSON file as its exclusive persistence mechanism.
- The system is designed for a single-user, single-process environment with moderate transaction volumes.
- The accepted operational capacity for the current release is up to **10,000 historical transaction records**.
- Transaction retrieval, compound filtering, sorting, and pagination will be performed in application memory after loading the JSON dataset.
- Pagination will limit the number of records returned to the presentation layer but will not eliminate the computational cost of loading and processing the underlying transaction collection.
- The application must monitor the number of historical transaction records stored in the JSON ledger.

**Capacity warning:**

- When the transaction count reaches 9,000 records, the system must display a capacity warning informing the user that the application is approaching its supported transaction limit.

**Maximum capacity enforcement:**

- The application must enforce a maximum capacity of 10,000 historical transaction records.
- Once the ledger reaches 10,000 records, the system must reject any new INCOME, EXPENSE, TRANSFER, or REVERSAL operation that would increase the count beyond the supported limit.
- Capacity validation must occur before proposed account balance mutations, ledger modifications, or persistence operations.
- Existing in-memory and persisted states must remain unchanged following capacity rejection.
- The user must receive a clear notification explaining that transaction capacity has been reached and that a persistence architecture reassessment is required.

**Future migration path:**

- Transaction volumes exceeding the supported capacity will require an explicit architecture reassessment.
- SQLite is identified as the preferred migration path because it provides structured queries, indexing, and transactional capabilities.

---