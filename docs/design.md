# 1. Requirements Interpretation

## 1.1 Accounts

- **Req-1: Account Creation & Metadata**
  - The system must allow users to create multiple concurrent financial accounts.
  - The system must enforce and persist the following attributes for every account: a unique system identifier (ID), a user-defined account name, an account type (e.g., Bank, Savings, Cash, Mobile Wallet), and a creation timestamp.

- **Req-2: Account Retrieval (View & Inspect)**
  - The system must provide a list view of all active accounts belonging to the user.
  - The system must allow users to inspect a specific account to view its details, current balance, and associated transaction history.

- **Req-3: Account Modification**
  - The system must allow users to update the name of an existing account.

- **Req-4: Account Activation/Deactivation**
  - The system must allow users to deactivate an account, changing its state to inactive and removing it from the default active accounts list view.
  - The system must allow users to reactivate an account, changing its state to active from inactive and puting it in the default active accounts list view.
  - (Note: The validation logic requiring a 0.00 balance will be fully detailed in Section 2: Business Rules).

## 1.2 Income

- **Req-5: Income Recording (Metadata)**
  - The system must allow users to record income transactions(deposits).
  - The system must capture and validate the following inputs for each income entry: transaction amount (positive monetary value), target financial account, transaction date/time, and a descriptive label (e.g., "Salary").

- **Req-6: Account Balance Mutation**
  - Upon successfully recording income, the system must immediately increment the balance of the designated target account by the transaction amount.

- **Req-7: Transaction Ledger Logging**
  - The system must write every income record to the user's permanent, immutable transaction history.
  - System Note: The account balance update (Req-6) and the transaction ledger log (Req-7) must execute as an atomic transaction (either both succeed or both fail) to prevent data mismatch.

## 1.3 Expenses

- **Req-8: Expense Recording (Metadata)**
  - The system must allow users to record expense transactions.
  - The system must capture and validate the following inputs for each expense entry: transaction amount (positive monetary decimal value), source financial account, transaction date/time, expense category (e.g., Food, Bills), and an optional descriptive label (e.g., "Groceries").

- **Req-9: Account Balance Mutation**
  - Upon successfully recording an expense, the system must immediately decrement the balance of the designated source account by the transaction amount.
  - System Note: The system's behavior regarding whether an account balance is allowed to drop below 0.00 (overdraft) will be defined in Section 4: Business Rules.

- **Req-10: Transaction Ledger Logging**
  - The system must write every expense record to the user's permanent, immutable transaction history.
  - System Note: The account balance update (Req-9) and the transaction ledger log (Req-10) must execute as an atomic database transaction.

## 1.4 Transfers

- **Req-11: Transfer Recording (Metadata)**
  - The system must allow users to record internal transfer transactions between their own accounts.
  - The system must capture and validate the following inputs: a source account (sender), a distinct target account (recipient), a transaction amount (positive monetary decimal value), and a transaction date/time.
  - The system must enforce that the source account and target account are not the same entity.

- **Req-12: Dual Account Balance Mutation**
  - Upon execution, the system must perform a simultaneous multi-account adjustment: decrement the source account balance and increment the target account balance by the transaction amount.
  - The system must guarantee that the net sum of both accounts remains unchanged after the mutation.

- **Req-13: Independent Transaction Classification**
  - The system must log the transfer to the immutable transaction history using a specific classification type (TRANSFER).
  - The system must isolate TRANSFER types from standalone INCOME or EXPENSE totals to prevent artificial inflation of financial reports.
  - System Note: The dual balance updates (Req-12) and the ledger logging (Req-13) must execute as a single atomic database transaction.

## 1.5 Transaction History

- **Req-14: Comprehensive Transaction Ledger View**
  - The system must provide a centralized transaction history ledger containing all historical financial activity for the user.
  - Every transaction record in the ledger must explicitly display: unique transaction ID, classification type (INCOME, EXPENSE, TRANSFER), timestamp, amount, primary account(s) involved, category (mandatory for expenses), and an optional descriptive label.

- **Req-15: History Optimization & Scalability (Large Data Volumes)**
  - To ensure performance under large volumes of data, the system must implement server-side pagination, defaulting to 25 records per page.
  - The system must display records sorted in reverse-chronological order (newest transactions first) by default.

## 1.6 Search and Filtering

- **Req-17: Compound Filter Engine**
  - The system must support the dynamic combination of multiple filter parameters within a single ledger request.
  - The system must execute queries utilizing the following filtering criteria:
    - **Temporal:** Specific date or inclusive date ranges.
    - **Categorical:** Transaction Type (INCOME, EXPENSE, TRANSFER) and expense categories.
    - **Entity-based:** Associated financial accounts.
    - **Quantitative Range:** Inclusive minimum and maximum monetary amounts (e.g., Amount >= Min AND Amount <= Max).

- **Req-18: Graceful Empty-State Handling**
  - When a compound filter yields zero matches, the backend system must return an empty dataset payload (e.g., HTTP 200 with an empty list []) rather than an error block.
  - The user interface must display a clear, non-intrusive "No matching transactions found" state with an option to reset filters.

## 1.7 Balances

- **Req-19: Granular Account Balances**
  - The system must calculate and expose the real-time monetary balance of every individual active financial account.

- **Req-20: Total Aggregate Net Worth Display**
  - The system must provide a consolidated dashboard view displaying the user's aggregate net balance across all active accounts.

- **Req-21: Strict Mathematical Integrity**
  - The system must guarantee internal consistency such that the total aggregate balance strictly equals the sum of all individual active account balances at any given timestamp.
  - The values must update automatically and atomically across all views upon the successful recording of any income, expense, or transfer transaction.

## 1.8 Financial Reports

- **Req-22: Time-Bounded Financial Summary Engine**
  - The system must generate aggregated financial summaries bounded by a user-selected date range (start date and end date).

- **Req-23: Core Reporting Metrics**
  - For the selected period, the system must calculate and display:
    - **Total Income:** The mathematical sum of all transactions classified as INCOME.
    - **Total Expenses:** The mathematical sum of all transactions classified as EXPENSE.
    - **Net Delta:** The net change calculated strictly as Total Income - Total Expenses.

- **Req-24: Categorical and Entity Breakdown**
  - The report must provide a breakdown of total expenditure grouped by expense category (e.g., Food, Utilities).
  - The report must display individual account activity, tracking the respective influx and outflux of funds for each active account during the period.

- **Req-25: Transfer Exclusion Rule**
  - The reporting engine must explicitly exclude transactions categorized as TRANSFER from both the Total Income and Total Expenses metrics to prevent artificial distortion of the user's cash flow analytics.

---
  
    
# 2. Business Rules

## 2.1 Accounts & Lifecycle Management

- **BR-01: Structural Integrity (Naming Constraints)**
  - Account names must not be empty strings, null, or consist solely of whitespace.
  - Account names must be between 4 and 20 characters in length.
  - Account names must be unique per user profile; the system must reject duplicate account names to prevent user confusion.

- **BR-02: Initial State and Typology**
  - Every newly initialized account must be automatically assigned an immutable unique identifier (UUID/ID) and an initial state status of ACTIVE.
  - The account type must strictly map to one of the allowed system enums (CASH, BANK, SAVINGS, MOBILE_WALLET). Any other string values must be rejected with a validation error.

- **BR-03: Reference Validation**
  - The system must reject any transaction attempt (Income, Expense, Transfer) that references a non-existent, malformed, or invalid Account ID or Name.

- **BR-04: Active List Isolation**
  - The standard account directory list view must exclusively query and display accounts possessing an ACTIVE status.

- **BR-05: Deactivation & Invalidation Isolation**
  - An account can only transition to an INACTIVE (deactivated) state if its current calculated balance is exactly 0.00.
  - Once an account status transitions to INACTIVE, it must be completely blocked from participating in any new ledger modifications, including incoming income, outgoing expenses, or internal transfers as either a sender or a receiver.

## 2.2 Monetary Values & Validation Mechanics

- **BR-06: Monetary Representation and Precision Integrity**
    - All monetary values must be internally represented and stored as integers in the smallest currency denomination (Kobo).
    - During input processing, valid Naira amounts must be converted into Kobo by multiplying the decimal amount by 100.
    - All financial calculations, including account balance mutations, transfers, and financial aggregations, must operate exclusively on integer Kobo values.
    - During data presentation, stored Kobo values must be converted back into Naira by dividing by 100 and formatted to exactly two decimal places.
    - The system must prohibit floating-point arithmetic in all financial calculations to eliminate precision-related discrepancies.

- **BR-07: Data Type & Range Constraints**
  - The system must reject any transaction amount input that contains non-numeric characters (alphabets, symbols), empty strings, or null values.
  - The system must strictly enforce that all transaction amounts are positive numbers strictly greater than zero (Amount > 0.00). Zero and negative inputs must be blocked.

- **BR-08: Numeric Precision and Scale (Currency Guard)**
  - The system must evaluate all monetary figures up to exactly two decimal places of scale (representing Naira and Kobo).
  - Any user input exceeding two decimal places must be rejected with a validation error to prevent floating-point calculation mismatches.

- **BR-09: Transaction Ceiling (Upper Bound Safety)**
  - To mitigate overflow vulnerabilities in arithmetic calculations, the system must reject any single transaction amount exceeding a safety ceiling of ₦99,999,999.99.

- **BR-10: Balance Sufficiency (Overdraft Prevention)**
  - For EXPENSE and TRANSFER operations, the system must verify that the designated source account holds a balance equal to or greater than the intended transaction amount.
  - If the transaction amount exceeds the current account balance, the operation must be aborted, and an insufficient funds validation error returned.

- **BR-11: Financial State Authority and Balance Consistency**
    - The transaction ledger shall serve as the authoritative source of financial truth for all account balances.
    - The acc_bal attribute stored within each account shall serve as a cached representation of the account's current calculated balance.
    - Every successful INCOME, EXPENSE, or TRANSFER operation must update the affected account balance and append the corresponding transaction record as a single atomic operation.
    - The system must guarantee that the stored account balance remains mathematically consistent with the cumulative net effect of all associated historical ledger transactions.
    - If a discrepancy is detected between the stored account balance and the ledger-derived balance, the ledger-derived value shall take precedence, and the stored balance must be recalculated and corrected.

- **BR-12: Balance Reconciliation**
    - The system must provide an internal reconciliation mechanism capable of recalculating account balances using historical transaction records.
    - The reconciliation process must account for all INCOME, EXPENSE, and TRANSFER transactions associated with each account.
    - The reconciliation process must identify discrepancies between stored balances and ledger-derived balances.
    Any detected discrepancy must be corrected using the ledger-derived balance.

## 2.3 Transfer Mechanics

- **BR-13: Self-Transfer Prevention**
  - The system must reject transfer operations where the unique identifier (ID) of the source account matches the unique identifier of the destination account.

- **BR-14: Multi-Account Lifecycle and Existence Check**
  - The system must verify the existence of both accounts; the operation must fail if either the source account ID or the destination account ID does not exist in the persistence layer.
  - The system must block the transaction if either the source account or the destination account holds an INACTIVE status.

- **BR-15: Transfer Quantification & Global Constraints**
  - All transfer amounts must adhere strictly to the numeric validation, scale, and threshold limits established in Section 2.2 (BR-06, BR-07, and BR-08).

- **BR-16: Asset Sufficiency (Overdraft Enforcement)**
  - The system must confirm that the source account's current balance is greater than or equal to the transfer amount.
  - If the source account balance is insufficient, the transaction must be aborted, no database states may be mutated, and an explicit INSUFFICIENT_FUNDS error payload returned.

## 2.4 Date and Timestamp Validation

- **BR-17: Date Format and Structural Integrity**
    - The system must validate that all incoming transaction dates conform strictly to the ISO 8601 date format (YYYY-MM-DD).
    Any malformed date strings must be rejected with a validation error.

- **BR-18: Calendar Consistency Checks**
  - The system must execute real-calendar validation checks on all inputs. Inputs representing non-existent calendar dates (e.g., 2026-02-30 or 2026-11-31) must be intercepted and rejected.

- **BR-19: Future-Date Restriction**
    - The system must compare all transaction dates against the current system date.
    - The system must explicitly reject any transaction containing a date later than the current calendar date.
    - Transactions dated on the current calendar date or any previous valid calendar date must be accepted.

---
	
# 3. Assumptions

- **ASM-01: Single-User Execution Environment**
  - The system assumes an isolated, local execution architecture dedicated to a single user profile. Consequently, remote user authentication layers, role-based access controls (RBAC), and session tokens are completely decoupled from the system's current design scope.

- **ASM-02: Ex Post Facto Ledger Recording**
  - The system assumes that all manually input data reflects transactions that have already concluded in the real world. This baseline behavior justifies the strict programmatic rejection of future-dated timestamps.

- **ASM-03: Single Threaded Execution & File Access**
  - The system assumes synchronous, single-threaded execution by one terminal process at a time. It assumes no concurrent file-locking conflicts or race conditions will occur on the host machine.

- **ASM-04: Environment and Runtime Compatibility**
  - It is assumed that the application runs within a standard command-line interface terminal (CLI) with an active Python 3.10 (or higher) runtime environment installed on the host operating system.

# 4. Identified Ambiguities

- **AMB-01: Terminal Interaction Pattern**
  - **Ambiguity:** The prompt defines functional capabilities but does not specify the method of user input collection within the CLI environment.
  - **Resolution:** We have resolved this by opting for a synchronous interactive menu loop using Python's native input() utility, rather than parsing raw CLI flags.

- **AMB-02: Structural Casing for Uniqueness Constraints**
  - **Ambiguity:** The prompt states that duplicate account names must be rejected but does not clarify string evaluation limits regarding capitalization.
  - **Resolution:** The system will strictly enforce case-insensitive evaluation across all string boundaries (e.g., "Cash" matches "cash") to proactively prevent data redundancy.

- **AMB-03: Persistence**
  - **Ambiguity:** The prompt states that transaction history must remain useful over time but does not specify a storage medium.
  - **Resolution:** The system persists data locally using a structured JSON flat-file/SQLite database rather than keeping it strictly in-memory, ensuring user data survives terminal sessions.

# 5. Architecture & Layout Blueprint

## 5.1 Three-Tier Layer Separation

- **Presentation Layer (ui/):** Manages terminal rendering, command-line display, and collects synchronous string inputs via input(). This layer is forbidden from executing math adjustments or parsing file files directly.

- **Business Logic Layer (models/):** Implements code validation boundaries, evaluates constraints (e.g., insufficient balances, string formatting rules), and tracks application execution states.

- **Data Access Layer (file_manager/):** Isolates all disk I/O mutations. Handles loading parsing tasks and serializing JSON payloads to flat storage files securely.

### Data Flow Direction

```text
[ Presentation Layer (UI) ] ──> [ Business Logic Layer ] <──> [ Data Access Layer ]
````

## 5.2 Project Structure

text

```text
wallet_manager/
│
├── main.py                 # Application entry-point and central bootstrapper
│
├── ui/                     # Presentation Tier
│   └── ui.py               # Menu engine loop and terminal text input collectors
│
├── models/                 # Business Logic Tier
│   ├── wallet_engine.py    # Main coordinator executing core workflows
│   ├── account.py          # Entity validator enforcing account rules
│   └── transaction.py      # Entity validator enforcing ledger rules
│
├── file_manager/           # Data Access Tier
│   └── storage.py          # Plain text JSON reading and rewriting utilities
│
└── utils/                  # Shared cross-cutting components
    └── validators.py       # Reusable currency scale and ISO date format regex utilities
```

## 5.3 Data Structure

json

```json
{
  "accounts": {
    "acc_aBc12": {
      "id": "acc_aBc12",
      "acc_name": "First Bank",
      "acc_type": "SAVINGS",
      "acc_bal": 525000,
      "created_at": "2026-11-10"
    },
    "acc_cBg5i": {
      "id": "acc_cBg5i",
      "acc_name": "Savings Acc",
      "acc_type": "SAVINGS",
      "acc_bal": 500000,
      "created_at": "2026-11-10"
    }
  },
  "transactions": [
    {
      "id": "trx_123Df",
      "amount": 25000,
      "trx_type": "EXPENSE",
      "category": "Food",
      "desc": "Groceries",
      "source_acc_id": "acc_aBc12",
      "target_acc_id": null,
      "timestamp": "2026-11-10"
    },
    {
      "id": "trx_1oerf",
      "amount": 1050000,
      "trx_type": "INCOME",
      "category": "Salary",
      "desc": "Monthly paycheck",
      "source_acc_id": null,
      "target_acc_id": "acc_aBc12",
      "timestamp": "2026-11-10"
    },
    {
      "id": "trx_0q1wS",
      "amount": 500000,
      "trx_type": "TRANSFER",
      "category": "Internal Transfer",
      "desc": "Moving to savings",
      "source_acc_id": "acc_aBc12",
      "target_acc_id": "acc_cBg5i",
      "timestamp": "2026-11-10"
    }
  ]
}
```

# 6. Persistence Architecture & Integrity Guard

## Serialization Lifecycle (json.dump / json.load)

- **Data Extraction (Deserialization):** Upon application boot, the Data Access Layer reading utility utilizes Python's native json.load() function to read the local storage file. It parses the raw character blocks into an operational native Python dictionary structure for business engine execution.
- **Data Compression (Serialization):** When transaction logs are updated, state properties are converted back into a valid JSON string mapping payload via Python’s json.dump() method with a strict indentation format to preserve human-readable scannability.

## Atomic Write Fail-Safe Strategy

- To prevent structural data corruption during file I/O operations (e.g., if the user accidentally closes the terminal execution stream mid-write), the system forbids writing directly into the active database file.
- The application must write the fully serialized payload string into a hidden temporary staging file first (.storage.json.tmp).
- Once the I/O system verifies a complete, non-truncated flush to disk, it executes a low-level atomic rename operation using os.replace(".storage.json.tmp", "storage.json"). This ensures that even if a power loss occurs, the application state remains stable, rollback-compliant, and uncorrupted.

6.2 In-Memory State Consistency and Transaction Commit
The system must never directly mutate the active in-memory application state before successfully persisting the corresponding changes to disk.
Before executing any financial transaction, the Business Logic Layer must create a temporary copy of the current application state.
All proposed account balance mutations and transaction ledger additions must be applied exclusively to this temporary state.
The Data Access Layer must serialize and persist the complete temporary state using the established staging-file and atomic replacement strategy.
Only after successful completion of the file replacement operation may the Business Logic Layer commit the temporary state as the new active in-memory application state.
If persistence fails at any stage, the temporary state must be discarded, the original in-memory state must remain unchanged, and a DatabaseWriteException must be raised.
The user interface must display an appropriate error message without reporting the transaction as successful.

# 7.0 Error Handlling

## 7.1 Input & Domain Validation Matrix (Business Layer)

The system wraps standard, low-level Python runtime errors into explicit, high-level custom domain exceptions to ensure the user interface receives clean validation targets without crashing the execution loop.

| Expected Error | Root Cause Context | Trapped Native Exception | Custom Domain Exception Raised | User-Facing Console Feedback |
| --- | --- | --- | --- | --- |
| Invalid Amount Entry | Input contains non-numeric characters, invalid decimal structures, empty values, or amounts exceeding 2 decimal places. | InvalidOperation during Decimal conversion; ValueError during monetary validation and conversion. | InvalidAmountError | "Error: Amount must be a valid positive number with up to 2 decimal places." |
| Malformed Account Name | Empty strings, whitespace, or strings under 4 or over 20 characters. | Failure during internal string length check. | InvalidAccountNameError | "Error: Account name cannot be blank and must be between 4 and 20 characters long." |
| Invalid Account Type | Input fails to match allowed types (CASH, BANK, etc.). | Value mapping check fails against allowed Enums. | InvalidAccountTypeError | "Error: Invalid account type. Must be one of: Cash, Bank, Savings, or Mobile Wallet." |
| Invalid Account Status | Input fails to match allowed states (ACTIVE, INACTIVE). | Value mapping check fails against state Enums. | InvalidAccountStatusError | "Error: System action rejected. Account state must be either ACTIVE or INACTIVE." |
| Invalid Transaction Date | Input contains malformed dates, non-existent calendar dates, or dates later than the current system date. | ValueError during parsing via datetime.strptime() or future-date validation. | InvalidDateError | "Error: Invalid transaction date. Please use YYYY-MM-DD and ensure the date is not in the future." |
| Invalid Transaction Type | Input fails to match allowed operational states. | Value mapping check fails against transaction Enums. | InvalidTransactionTypeError | "Error: System action rejected. Transaction type must be one of: INCOME, EXPENSE, or TRANSFER." |
| Invalid Account / Transaction ID | Empty string inputs or non-existent unique keys. | Membership key lookup failure (id not in dict). | EntityNotFoundError | "Error: System action rejected. The requested account or transaction ID does not exist." |
| Invalid Category | Selected category does not match the valid, allowed options list. | Value verification fails membership list evaluation. | InvalidCategoryError | "Error: System action rejected. Please select a valid transaction category." |
| Insufficient Funds | Transaction amount exceeds the available balance during a withdrawal or transfer. | Evaluation check evaluates to Amount \> Account.balance. | InsufficientFundsError | "Error: Transaction aborted. Insufficient funds in the selected source account." |
| Self Transfer Violation | User attempts to move money to the exact same account. | Equality match evaluates to Source\_ID == Target\_ID. | SelfTransferError | "Error: Transfer rejected. Source and destination accounts cannot be the same entity." |
| Inactive Account Mutation | User attempts to post an entry involving a deactivated account. | Lifecycle validation check flags status as INACTIVE. | InactiveAccountError | "Error: Action blocked. Cannot post transactions to or from a deactivated account." |

## 7.2 Storage & Persistence Exceptions (Data Access Layer)

The Data Access Layer traps low-level operating system and file system anomalies, translating them into controlled database exceptions or executing silent self-healing actions.

| Expected Error | Root Cause Context | Trapped Native Exception | Custom Exception Raised | User-Facing / System Resolution Feedback |
| --- | --- | --- | --- | --- |
| Missing Storage Ledger | Application is initialized for the first time, or the storage file was manually deleted. | FileNotFoundError during execution of open(). | None (Gracefully Handled) | System Action: Intercepted silently. The Data Access Layer automatically creates the missing directory and initializes a clean file containing empty structures ({"accounts": {}, "transactions": \[\]}). |
| Corrupted JSON Payload | Manual tampering or partial disk writes left broken syntax inside the file. | json.JSONDecodeError during data load. | DatabaseCorruptedException | "Fatal Error: The local database file is corrupted and cannot be parsed. Please check storage.json syntax or restore from a backup." (Application safely terminates) |
| Write Permission Locked | Host OS has flagged the file as read-only, or another background process blocked it. | PermissionError or OSError during a flush or write step. | DatabaseWriteException | "Error: Disk write access denied. The system cannot save your changes. Please check folder write permissions." |

## 7.3 Top-Level Catch-All Engine

To prevent raw Python tracebacks from leaking into the terminal under unexpected conditions, the main entry point (`main.py`) wraps the execution menu loop inside a global catch-all safety block:

python

```python
try:
    # Run interactive console menu loop
    app.run()
except Exception as e:
    print("\n[CRITICAL ERROR] An unexpected system failure occurred.")
    print("Please restart the application. If issues persist, contact support.")
    # In a production scope, the full trace 'e' would be piped to an internal 'app.log' file here.
    sys.exit(1)
```

# 8.0 Testing Strategy

To guarantee system stability, mathematical integrity, and compliance with all business rules, the application implements a multi-tiered automated testing suite utilizing Python's built-in unittest framework. Test configurations explicitly address Happy Paths (optimal inputs), Failure Paths (invalid data rejection), and Boundary Edge Cases.

## 8.1 Unit Testing (Isolated Functional Integrity)

Unit tests isolate specific business functions and validation hooks. Components are tested independently by mocking out disk dependencies to verify specific exceptions are raised.

| Targeted Module | Strategy | Test Function Identifier | Test Parameters / Inputs | Expected Terminal State / Exception |
| --- | --- | --- | --- | --- |
| Account Creation | Happy Path | test\_create\_account\_success | id="acc\_1w", name="Polaris Bank", type="BANK", bal=0.00 | Account instance initialized successfully with status ACTIVE. |
| Account Creation | Failure Path | test\_create\_account\_name\_too\_short | id="acc\_1w", name="Pol", type="BANK", bal=0.00 | Raises InvalidAccountNameError \[BR-01 Compliance\] |
| Account Creation | Edge Case | test\_create\_account\_exact\_lower\_bound | id="acc\_1w", name="Opay", type="MOBILE\_WALLET", bal=0.00 | Account instance initialized successfully (Exactly 4 characters). |

## 8.2 Integration Testing (Cross-Layer Subsystem Communication)

Integration tests assess the communication pathways between distinct structural tiers, specifically verifying that the Business Logic Layer updates and reads from the Data Access Layer (storage.py) correctly.

| Targeted Interaction | Strategy | Test Function Identifier | Scenario Setup / Inputs | Expected Integration Outcome |
| --- | --- | --- | --- | --- |
| Atomic Entry Lifecycle | Happy Path | `test_business_action_triggers_file_flush` | Post a valid INCOME entry via `wallet_engine.py`. | 1\. Temporary application state is created. 2. Account balance and transaction ledger are updated in the temporary state. 3. `storage.py` successfully writes the serialized state using atomic file replacement. 4. New state is committed to active memory. |
| Transaction Conflict | Failure Path | `test_balance_check_blocks_file_write` | Attempt an over-balance EXPENSE transaction. | 1\. Engine intercepts balance violation. 2. Throws `InsufficientFundsError`. 3. No in-memory state is mutated. 4. Disk write is bypassed. |
| Persistence Failure | Failure Path | `test_failed_persistence_preserves_memory_state` | Attempt a valid INCOME transaction while simulating a file write failure. | 1\. `DatabaseWriteException` is raised. 2. Temporary state is discarded. 3. Original in-memory balance and ledger remain unchanged. 4. Existing JSON storage remains unchanged. 5. User receives a failure notification. |

## 8.3 End-to-End (E2E) Testing (Terminal Simulation workflow)

End-to-End tests simulate a user interacting with the live CLI menu interface.

- **Execution Framework:** These tests utilize Python's unittest.mock.patch utility to inject sequential inputs directly into the standard console stream (sys.stdin) and inspect the output printed to the terminal console (sys.stdout).
- **Test Case Example:** A complete end-to-end script simulation handles booting the application menu, choosing option 1 to build a new account, option 2 to log a transaction against it, and option 5 to view the balance history sheet, confirming the text matches across the user path.

# 9.0 Explicit Out-of-Scope Decisions

To ensure a reliable and focused implementation within the project timeline, the following technical capabilities have been explicitly designated as out-of-scope. No code blocks or structures will be engineered to support these features in the current release cycle.

- **Identity & Session Security**
  - **User Authentication & Authorization:** In alignment with ASM-01 (Single-User Scope), the application will not feature registration screens, password hashing forms, multi-user login gates, or login session handlers.
- **Financial & Currency Scope Boundaries**
  - **Multi-Currency Frameworks:** The system is built exclusively around a single fiat currency baseline (Nigerian Naira - ₦). Cross-border currency conversions, exchange-rate calculations, and multi-currency ledger balances are completely excluded.
  - **Automated / Recurring Transactions:** The ledger only handles manual, real-time entries. Automated standing orders, recurring bill schedulers, or future calendar salary automations are out of scope.
- **Infrastructure & Deployment Interfaces**
  - **Web, Mobile, or Graphical Deployment:** The presentation layer is decoupled from graphical user interfaces (GUIs). Web hosting architectures, RESTful API servers, and mobile framework adaptations are omitted; the app is strictly a localized Python Command-Line Interface (CLI).
- **External Ecosystem Integrations**
  - **External Open Banking APIs:** The engine operates inside a closed data loop. The application will not connect to live banking webhooks, external payment gateways (such as Mono, Flutterwave, or Stripe), or real-time card authorization APIs.
  - **Artificial Intelligence Modules:** Categorization and financial reports rely entirely on strict user inputs and standard relational logic. Predictive budget tracking, AI-powered financial advisory chat systems, and automated expense category guessing engines are omitted.