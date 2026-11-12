# Personal Finance Wallet Manager

## Software Requirements Specification (SRS), Business Rules & Technical Architecture

# 1\. Requirements Interpretation

## 1.1 Accounts

- **Req-1: Account Creation & Metadata**
  - The system must allow users to create multiple concurrent financial accounts.
  - Every account must have a unique system-generated identifier (ID), a user-defined account name, an account type, a creation timestamp, an initial balance of zero Kobo, and an account status.
  - Supported account types are BANK, SAVINGS, CASH, and MOBILE\_WALLET.
  - Every newly created account must have an initial status of ACTIVE.
- **Req-2: Account Retrieval (View & Inspect)**
  - The system must provide a list view of all active accounts belonging to the user.
  - The system must allow users to inspect individual accounts, displaying their details, current balance, account status, and associated transaction history.
- **Req-3: Account Modification**
  - The system must allow users to update the name of an existing account.
  - Updated account names must comply with the naming constraints defined in BR-01.
- **Req-4: Account Activation/Deactivation**
  - The system must allow users to deactivate an account, changing its status to INACTIVE and removing it from the default active accounts list.
  - The system must allow users to reactivate an inactive account, changing its status to ACTIVE and restoring it to the default active accounts list.
  - Deactivation is permitted only when the account's ledger-derived balance is exactly zero Kobo.
  - Reactivation must not alter the account's historical transactions or balance.

## 1.2 Income

- **Req-5: Income Recording (Metadata)**
  - The system must allow users to record income transactions.
  - The system must capture and validate the following inputs:
    - Transaction amount (positive monetary value).
    - Target financial account.
    - Transaction date (YYYY-MM-DD).
    - Optional descriptive label (e.g., Salary).
- **Req-6: Account Balance Mutation**
  - Upon successfully recording income, the system must increment the balance of the designated target account by the transaction amount.
- **Req-7: Transaction Ledger Logging**
  - The system must write every income record to the user's permanent transaction history.
  - Income records must be classified as INCOME.
  - The account balance mutation and ledger update must be treated as one logical transaction.
  - Both changes must be persisted together through the staging-file and atomic replacement strategy.
  - The active in-memory state must only be updated after successful persistence.

## 1.3 Expenses

- **Req-8: Expense Recording (Metadata)**
  - The system must allow users to record expense transactions.
  - The system must capture and validate:
    - Transaction amount (positive monetary decimal value).
    - Source financial account.
    - Transaction date (YYYY-MM-DD).
    - Expense category (e.g., Food, Bills, Utilities).
    - Optional descriptive label (e.g., Groceries).
- **Req-9: Account Balance Mutation**
  - Upon successfully recording an expense, the system must decrement the balance of the designated source account by the transaction amount.
  - The system must prevent overdrafts in accordance with BR-10.
- **Req-10: Transaction Ledger Logging**
  - The system must write every expense record to the user's permanent transaction history.
  - Expense records must be classified as EXPENSE.
  - The account balance mutation and ledger update must be treated as one logical transaction and persisted together.

## 1.4 Transfers

- **Req-11: Transfer Recording (Metadata)**
  - The system must allow users to record internal transfers between their own accounts.
  - The system must capture and validate:
    - Source account (sender).
    - Target account (recipient).
    - Transaction amount (positive monetary value).
    - Transaction date (YYYY-MM-DD).
    - Optional descriptive label.
  - The source and target accounts must be distinct entities.
- **Req-12: Dual Account Balance Mutation**
  - Upon execution, the system must decrement the source account balance and increment the target account balance by the same transaction amount.
  - Both account mutations must occur as one atomic logical operation.
  - The combined balance of the two accounts must remain unchanged after the transfer.
- **Req-13: Independent Transaction Classification**
  - The system must classify internal transfers as TRANSFER in the immutable transaction history.
  - TRANSFER transactions must be excluded from standalone INCOME and EXPENSE totals.
  - The source and target account references must both be recorded.
  - The account mutations and corresponding ledger record must be persisted together.

## 1.5 Transaction History

- **Req-14: Comprehensive Transaction Ledger View**
  - The system must provide a centralized transaction history ledger containing all historical financial activity.
  - Every transaction record must explicitly contain:
    - Unique transaction ID.
    - Classification type (INCOME, EXPENSE, TRANSFER).
    - Transaction date.
    - Amount in integer Kobo.
    - Relevant account reference(s).
    - Category, mandatory for EXPENSE transactions.
    - Optional descriptive label.
  - Historical transaction records must remain available even when an associated account becomes inactive.
- **Req-15: Transaction History Pagination and Scalability**
  - The system must implement application-level pagination when retrieving transaction history.
  - The default page size must be 25 records.
  - Users must be able to navigate between available transaction history pages through the CLI.
  - Transactions must be sorted in reverse-chronological order (newest first) by default.
  - Pagination must be applied only after the relevant filtering and sorting operations have been completed.

## 1.6 Search and Filtering

- **Req-16: Compound Filter Engine**
  - The system must support the dynamic combination of multiple filter parameters within a single transaction history request.
  - Supported filtering criteria must include:
    - **Temporal:** Specific dates or inclusive date ranges.
    - **Categorical:** Transaction type (INCOME, EXPENSE, TRANSFER) and expense category.
    - **Entity-based:** Associated financial accounts.
    - **Quantitative:** Inclusive minimum and maximum monetary amounts.
  - Multiple active filters must be evaluated together using logical AND conditions.
  - Account-based filtering must consider both source and target account references where applicable.
- **Req-17: Graceful Empty-State Handling**
  - When a search or compound filter produces zero matching transactions, the Business Logic Layer must return an empty collection rather than raising an exception.
  - The presentation layer must display a clear message: "No matching transactions found."
  - The CLI must provide an option to reset active filters and return to the unfiltered transaction history.

## 1.7 Balances

- **Req-18: Granular Account Balances**
  - The system must calculate and expose the current monetary balance of every individual account.
  - The ledger-derived balance must serve as the authoritative value.
- **Req-19: Total Aggregate Net Worth Display**
  - The system must provide a consolidated dashboard displaying the aggregate net balance across all active accounts.
- **Req-20: Strict Mathematical Integrity**
  - The system must guarantee that the aggregate balance equals the sum of all individual active account balances.
  - Balance information must update automatically following successful income, expense, and transfer operations.
  - Balance changes must remain consistent across account inspection, account listings, and dashboard views.

## 1.8 Financial Reports

- **Req-21: Time-Bounded Financial Summary Engine**
  - The system must generate financial summaries bounded by a user-selected start date and end date.
  - Both dates must be inclusive.
- **Req-22: Core Reporting Metrics**
  - For the selected reporting period, the system must calculate:
    - **Total Income:** Sum of transactions classified as INCOME.
    - **Total Expenses:** Sum of transactions classified as EXPENSE.
    - **Net Delta:** Total Income minus Total Expenses.
- **Req-23: Categorical and Entity Breakdown**
  - The report must provide a breakdown of total expenditure grouped by expense category.
  - The report must display individual account activity, including incoming and outgoing funds for each active account during the selected period.
- **Req-24: Transfer Exclusion Rule**
  - The reporting engine must explicitly exclude TRANSFER transactions from Total Income and Total Expenses.
  - Transfers must not artificially inflate or reduce the user's reported cash flow.
  - Account-level activity reports must nevertheless include transfers as incoming or outgoing account movements.

---

# 2\. Business Rules

## 2.1 Accounts & Lifecycle Management

### BR-01: Structural Integrity (Naming Constraints)

- Account names must not be empty, null, or consist exclusively of whitespace.
- Account names must contain between 4 and 20 characters, inclusive.
- Account names must be unique per user profile.
- Uniqueness evaluation must be case-insensitive.
- Leading and trailing whitespace must be removed before validation and persistence.
- Duplicate names must be rejected with an appropriate validation error.

### BR-02: Initial State and Typology

- Every newly created account must automatically receive a unique system-generated identifier.
- UUID-based identifiers or another collision-resistant unique ID mechanism may be used.
- Every new account must have an initial status of ACTIVE.
- Every new account must have an initial balance of zero Kobo.
- Account types must strictly map to the following allowed system enums:
  - CASH
  - BANK
  - SAVINGS
  - MOBILE\_WALLET
- Any other account type must be rejected.

### BR-03: Reference Validation

- The system must reject any transaction referencing a non-existent, malformed, or invalid account ID.
- Account references must be validated against the persisted account collection.
- Account names must not be treated as substitutes for unique account identifiers during transaction processing.

### BR-04: Active List Isolation

- The standard account directory must exclusively display accounts with ACTIVE status.
- Inactive accounts must remain accessible through an appropriate account history or inactive-account inspection option.

### BR-05: Deactivation and Invalidation Isolation

- An account may transition from ACTIVE to INACTIVE only if its ledger-derived balance is exactly zero Kobo.
- The cached `acc_bal` value must not serve as the sole authority for this validation.
- An inactive account must be blocked from participating in new financial transactions.
- This restriction applies to incoming income, outgoing expenses, and internal transfers as either source or target.
- Reactivation must restore the account's ACTIVE status without changing its historical ledger records.
- Account deactivation and reactivation must be persisted using the established atomic file replacement mechanism.

## 2.2 Monetary Values and Validation Mechanics

### BR-06.1: Monetary Representation and Precision Integrity

- All monetary values must be internally represented and stored as integers in the smallest currency denomination, Kobo.
- One Nigerian Naira equals 100 Kobo.
- During input processing, valid Naira amounts must be converted into Kobo by multiplying the decimal amount by 100.
- All financial calculations, including account balance mutations, transfers, balance reconciliation, and financial aggregations, must operate exclusively on integer Kobo values.
- During data presentation, Kobo values must be converted into Naira by dividing by 100 and formatted to exactly two decimal places.
- Binary floating-point arithmetic must be prohibited throughout all monetary processing.
- Monetary values must never be stored as floating-point numbers in JSON.

### BR-06.2: Decimal-to-Integer-Kobo Input Conversion Mechanism

- The application must parse user-entered Naira amounts using Python's `decimal.Decimal` type rather than binary floating-point types.
- Monetary input must initially be received as a string from the CLI.
- Before conversion, the application must validate that the input:
  - Is a valid numeric monetary representation.
  - Is finite.
  - Is strictly greater than zero.
  - Contains no more than two decimal places.
  - Does not exceed the transaction ceiling established in BR-09.
- Following successful validation, the Decimal amount must be multiplied by 100.
- The resulting value must be converted into an integer representing Kobo.
- The integer Kobo value must be used for all subsequent storage, balance mutations, transfers, and financial calculations.
- Binary floating-point types must not be used at any stage of monetary processing.

**Illustrative conversion example:**

| User Input (Naira) | Decimal Calculation | Stored Value (Kobo) |
| --- | --- | --- |
| ₦100 | 100 × 100 | 10,000 |
| ₦250.50 | 250.50 × 100 | 25,050 |
| ₦1,250.75 | 1250.75 × 100 | 125,075 |
| ₦0.01 | 0.01 × 100 | 1 |

**Recommended Python implementation:**

python

```python
import re
from decimal import Decimal, InvalidOperation

def convert_to_kobo(user_input):
    if not isinstance(user_input, str):
        raise InvalidAmountError()

    cleaned_input = user_input.strip()

    # Accept ordinary decimal notation with at most
    # two digits after the decimal point.
    if not re.fullmatch(r"\d+(?:\.\d{1,2})?", cleaned_input):
        raise InvalidAmountError()

    try:
        amount = Decimal(cleaned_input)

        if not amount.is_finite() or amount <= 0:
            raise InvalidAmountError()

        if amount > Decimal("99999999.99"):
            raise InvalidAmountError()

        amount_in_kobo = amount * 100

        return int(amount_in_kobo)

    except (InvalidOperation, ValueError):
        raise InvalidAmountError()
```

The conversion function must return an integer Kobo value or raise `InvalidAmountError`. No financial operation may proceed using the original user-entered monetary string.

### BR-07: Data Type and Range Constraints

- The system must reject transaction amounts containing invalid characters, empty strings, or null values.
- Transaction amounts must be strictly positive.
- Zero and negative monetary values must be rejected.
- Currency symbols, commas, and other unsupported formatting characters must be rejected during input validation.

### BR-08: Numeric Precision and Scale (Currency Guard)

- The system must accept monetary input containing zero, one, or two decimal places.
- Inputs containing more than two decimal places must be rejected.
- The system must not silently round or truncate invalid monetary input.
- All validated monetary amounts must be converted to integer Kobo before financial calculations begin.

### BR-09: Transaction Ceiling (Upper-Bound Safety)

- The system must reject any single transaction exceeding ₦99,999,999.99.
- The maximum corresponding stored transaction amount is 9,999,999,999 Kobo.
- The ceiling must be enforced before any account balance mutation or persistence operation.

### BR-10: Balance Sufficiency (Overdraft Prevention)

- For EXPENSE and TRANSFER operations, the system must verify that the designated source account has a ledger-derived balance equal to or greater than the intended transaction amount.
- If the transaction amount exceeds the available balance:
  - The operation must be aborted.
  - No account balance may be modified.
  - No transaction record may be appended.
  - No persistence operation may be performed.
  - An `InsufficientFundsError` must be raised.

### BR-11: Financial State Authority and Balance Consistency

- The transaction ledger shall serve as the authoritative source of financial truth for all account balances.
- The `acc_bal` attribute stored within each account shall serve as a cached representation of its current calculated balance.
- Every successful INCOME, EXPENSE, or TRANSFER operation must update the affected account balance and append the corresponding transaction record as a single atomic logical operation.
- The system must guarantee that stored account balances remain mathematically consistent with the cumulative net effect of historical ledger transactions.
- If a discrepancy is detected between a stored account balance and its ledger-derived balance, the ledger-derived value must take precedence.
- The stored balance must be recalculated and corrected through the established persistence mechanism.
- Balance reconciliation must never modify historical transaction records.

### BR-11.1: Ledger-Derived Balance Calculation

The system must calculate each account's authoritative balance using the cumulative net effect of all associated historical transactions.

The calculation must follow these rules:

- **INCOME:** Add the transaction amount to the target account.
- **EXPENSE:** Subtract the transaction amount from the source account.
- **TRANSFER:** Subtract the transaction amount from the source account and add the same amount to the target account.

All calculations must use integer Kobo values exclusively.

The general balance calculation is:

**Calculated Balance = Total Income + Total Transfers In − Total Expenses − Total Transfers Out**

Where:

- Total Income represents all INCOME transactions credited to the account.
- Total Transfers In represents all TRANSFER transactions received by the account.
- Total Expenses represents all EXPENSE transactions debited from the account.
- Total Transfers Out represents all TRANSFER transactions sent from the account.

Additional rules:

- Newly created accounts must begin with a balance of zero Kobo.
- Inactive accounts must retain their historical balances and transaction associations.
- The calculated balance must serve as the authoritative reference during balance reconciliation, overdraft validation, and account lifecycle validation.
- An account must not be assigned an arbitrary initial balance outside the transaction ledger.

### BR-12: Balance Reconciliation

- The system must provide an internal reconciliation mechanism capable of recalculating account balances using historical transaction records.
- Reconciliation must account for all INCOME, EXPENSE, and TRANSFER transactions associated with each account.
- The process must identify discrepancies between stored balances and ledger-derived balances.
- Any discrepancy must be corrected using the ledger-derived value.
- Reconciliation corrections must be persisted safely using the atomic replacement strategy.
- Reconciliation must not generate artificial income, expense, or transfer transactions.

## 2.3 Transfer Mechanics

### BR-13: Self-Transfer Prevention

- The system must reject transfer operations where the unique identifier of the source account matches that of the destination account.
- The validation must be based on account IDs rather than account names.

### BR-14: Multi-Account Lifecycle and Existence Check

- The system must verify the existence of both source and destination accounts.
- The operation must fail if either account ID does not exist in the persistence layer.
- The system must block transfers if either account has INACTIVE status.

### BR-15: Transfer Quantification and Global Constraints

- All transfer amounts must comply with BR-06, BR-07, BR-08, and BR-09.
- Transfer amounts must be stored as integer Kobo.
- The same transaction amount must be debited from the source and credited to the destination.

### BR-16: Asset Sufficiency (Overdraft Enforcement)

- The system must confirm that the source account's ledger-derived balance is greater than or equal to the transfer amount.
- If the source account has insufficient funds:
  - The transaction must be aborted.
  - No database state may be mutated.
  - No transaction may be appended.
  - An explicit `InsufficientFundsError` must be returned.

## 2.4 Date Validation

### BR-17: Date Format and Structural Integrity

- The system must accept transaction dates exclusively in the ISO 8601 calendar date format: YYYY-MM-DD.
- The CLI must not require users to provide hours, minutes, seconds, timezone offsets, or timezone indicators.
- Valid date inputs must be parsed using Python's `datetime.date.fromisoformat()` method.
- The system must enforce the exact YYYY-MM-DD input structure before parsing.
- Inputs using alternative ISO 8601 representations must be rejected.
- Invalid inputs must raise `InvalidDateError`.

### BR-18: Calendar Consistency Checks

- The system must perform real-calendar validation on all transaction date inputs.
- Non-existent calendar dates, such as 2026-02-30 or 2026-11-31, must be rejected.
- Only valid calendar dates may proceed to future-date validation and transaction processing.

### BR-19: Future-Date Restriction

- The system must compare each validated transaction date against the current calendar date obtained from the dedicated date provider.
- Any transaction dated later than the current calendar date must be rejected.
- Transactions dated on the current date or any previous valid calendar date must be accepted.
- Date comparisons must use calendar dates rather than timezone-aware timestamps.

---

# 3\. Assumptions

### ASM-01: Single-User Execution Environment

- The system assumes an isolated, local execution architecture dedicated to a single user profile.
- Remote user authentication, role-based access controls (RBAC), and session tokens are outside the current design scope.

### ASM-02: Ex Post Facto Ledger Recording

- All manually entered financial records are assumed to represent transactions that have already concluded in the real world.
- This assumption justifies the rejection of future-dated transactions.

### ASM-03: Single-Threaded Execution and File Access

- The system assumes synchronous, single-threaded execution by one terminal process at a time.
- Concurrent file access, multi-process write conflicts, and race conditions are outside the supported execution model.
- The application does not guarantee multi-process concurrency control.

### ASM-04: Environment and Runtime Compatibility

- The application assumes execution within a standard command-line interface terminal.
- Python 3.10 or higher must be installed on the host operating system.

### ASM-05: Controllable System Date Provider

- The application must obtain the current calendar date through a dedicated date-provider function rather than directly accessing the system clock throughout the Business Logic Layer.
- During normal execution, the provider must return the host operating system's current local calendar date.
- The date provider must be replaceable or injectable during automated testing.
- All future-date validation must use the date returned by this provider to ensure consistent and reproducible results.

---

# 4\. Identified Ambiguities

### AMB-01: Terminal Interaction Pattern

- **Ambiguity:** The original requirements define functional capabilities but do not specify how users should interact with the application through the CLI.
- **Resolution:** The application will use a synchronous interactive menu loop implemented with Python's native `input()` utility rather than raw command-line argument parsing.

### AMB-02: Structural Casing for Uniqueness Constraints

- **Ambiguity:** The original requirements require unique account names but do not define how capitalization should affect uniqueness.
- **Resolution:** Account-name uniqueness will be evaluated case-insensitively.
- **Example:** "Cash" and "cash" will be treated as duplicate account names.
- Leading and trailing whitespace will be removed before uniqueness evaluation.

### AMB-03: Persistence Technology Selection

- **Ambiguity:** The original requirements specify persistent transaction history but do not prescribe a storage technology.
- **Resolution:** The application will use a structured JSON flat-file as its exclusive persistence mechanism. SQLite and other database management systems are excluded from the current implementation.

**Justification:**

JSON provides a lightweight, human-readable persistence mechanism suitable for the application's single-user, single-process execution environment. It integrates directly with Python's native `json` module and supports the existing Data Access Layer architecture.

**Trade-off:**

JSON does not provide native database indexing, query optimization, transactional rollback, or database-level concurrency controls. Consequently, large transaction histories will increase file parsing, serialization, filtering, and pagination costs.

### AMB-04: Transaction Category and Description Semantics

- **Ambiguity:** The requirements distinguish descriptive labels from expense categories but do not explicitly define how these fields apply to each transaction type.
- **Resolution:**
  - EXPENSE transactions must contain a category and may contain a descriptive label.
  - INCOME transactions may contain a descriptive label but do not require an expense category.
  - TRANSFER transactions may contain a descriptive label but do not require an expense category.
- The category field must be `null` for INCOME and TRANSFER records unless a future requirement explicitly introduces additional classification functionality.

### AMB-05: Account Balance Initialization

- **Ambiguity:** The original requirements do not define how newly created accounts acquire their initial balances.
- **Resolution:** All accounts must begin with zero Kobo. Initial funding must be recorded through a valid INCOME transaction rather than directly assigning a starting balance.

---

# 5\. Architecture and Layout Blueprint

## 5.1 Three-Tier Layer Separation

### Presentation Layer (`ui/`)

- Manages terminal rendering and command-line display.
- Collects synchronous string inputs using Python's `input()` utility.
- Displays validation errors, transaction confirmations, account information, and reports.
- Must not execute financial calculations or access JSON storage files directly.

### Business Logic Layer (`models/`)

- Implements business workflows and domain validation.
- Evaluates account, transaction, monetary, and date constraints.
- Calculates ledger-derived balances.
- Coordinates financial operations and state transitions.
- Manages proposed in-memory state changes before persistence.

### Data Access Layer (`file_manager/`)

- Isolates all disk input/output operations.
- Handles JSON deserialization and serialization.
- Executes staging-file writes and atomic replacement.
- Provides controlled persistence exceptions to the Business Logic Layer.

### Data/Execution Flow

text

```text
             USER
              |
              v
      PRESENTATION LAYER
           (ui.py)
              |
              v
      BUSINESS LOGIC LAYER
        (wallet_engine.py)
              |
              v
        DATA ACCESS LAYER
          (storage.py)
              |
              v
       LOCAL JSON STORAGE
```

## 5.2 Project Structure

text

```text
wallet_manager/
│
├── main.py                 # Application entry point and bootstrapper
│
├── ui/                     # Presentation Tier
│   └── ui.py               # Menu engine and terminal input collectors
│
├── models/                 # Business Logic Tier
│   ├── wallet_engine.py    # Main coordinator for core workflows
│   ├── account.py          # Account entity and validation rules
│   └── transaction.py      # Transaction entity and validation rules
│
├── file_manager/           # Data Access Tier
│   └── storage.py          # JSON reading and atomic writing utilities
│
└── utils/                  # Shared Components
    └── validators.py       # Reusable monetary and date validators
```

## 5.3 Data Structure

The application must persist account and transaction records using a structured JSON document.

**Illustrative JSON structure:**

json

```json
{
  "accounts": {
    "acc_aBc12": {
      "id": "acc_aBc12",
      "acc_name": "First Bank",
      "acc_type": "BANK",
      "acc_bal": 525000,
      "status": "ACTIVE",
      "created_at": "2026-11-10T09:30:00"
    },
    "acc_cBg5i": {
      "id": "acc_cBg5i",
      "acc_name": "Savings Acc",
      "acc_type": "SAVINGS",
      "acc_bal": 500000,
      "status": "ACTIVE",
      "created_at": "2026-11-10T10:00:00"
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
      "transaction_date": "2026-11-10"
    },
    {
      "id": "trx_1oerf",
      "amount": 1050000,
      "trx_type": "INCOME",
      "category": null,
      "desc": "Monthly paycheck",
      "source_acc_id": null,
      "target_acc_id": "acc_aBc12",
      "transaction_date": "2026-11-10"
    },
    {
      "id": "trx_0q1wS",
      "amount": 500000,
      "trx_type": "TRANSFER",
      "category": null,
      "desc": "Moving to savings",
      "source_acc_id": "acc_aBc12",
      "target_acc_id": "acc_cBg5i",
      "transaction_date": "2026-11-10"
    }
  ]
}
```

**Data structure constraints:**

- Account IDs must be unique.
- Transaction IDs must be unique.
- Account balances and transaction amounts must be integer Kobo values.
- Account statuses must be either ACTIVE or INACTIVE.
- Account creation timestamps must use a consistent ISO 8601 datetime representation.
- Transaction dates must use YYYY-MM-DD.
- INCOME records must have a target account and a null source account.
- EXPENSE records must have a source account and a null target account.
- TRANSFER records must have both source and target accounts.
- Only EXPENSE records require a non-null category.
- Account balances must be reconciled against the transaction ledger.

The JSON structure is illustrative. The actual account and transaction identifiers must be generated dynamically rather than copied from the example.

---

# 6\. Persistence Architecture and Integrity Guard

## 6.1 Serialization Lifecycle (`json.dump` / `json.load`)

**Data Extraction (Deserialization):**

- Upon application startup, the Data Access Layer must use Python's native `json.load()` function to read the local storage file.
- The raw JSON payload must be parsed into native Python dictionaries and lists for Business Logic Layer execution.
- Integer monetary values must remain integers after deserialization.

**Data Serialization:**

- When application state changes, the Data Access Layer must serialize the complete proposed state using Python's native `json.dump()` method.
- JSON serialization must use a consistent indentation format to preserve human readability.
- Monetary values must be serialized as JSON integers rather than floating-point numbers.

## 6.2 Atomic Write Fail-Safe Strategy

- The application must never write directly into the active JSON storage file during normal state updates.
- Instead, the complete proposed application state must first be written into a temporary staging file named `.storage.json.tmp`.
- The staging file must be created in the same directory as the destination `storage.json` file.
- After the staging file has been completely written and flushed, the Data Access Layer must execute `os.replace()` to atomically replace the active storage file.
- The replacement operation must occur only after successful serialization and staging-file writing.

**Atomic replacement guarantees:**

- Both files reside on the same filesystem.
- Readers will observe either the previous complete JSON file or the newly replaced complete JSON file, subject to the supported filesystem's atomic replacement guarantees.
- The destination file will not be exposed as a partially serialized JSON document during a successful atomic replacement.

**Durability limitation:**

Atomic replacement alone does not guarantee complete durability against every possible operating-system crash or power failure. Stronger crash-durability guarantees would require additional filesystem synchronization measures, including appropriate use of `fsync()`.

## 6.3 In-Memory State Consistency and Transaction Commit

- The system must never mutate the active in-memory application state before successfully persisting the corresponding changes to disk.
- Before executing a financial transaction, the Business Logic Layer must create a temporary copy of the current application state.
- Proposed account balance mutations and transaction ledger additions must be applied exclusively to this temporary state.
- The Data Access Layer must serialize and persist the complete temporary state using the staging-file and atomic replacement strategy.
- Only after successful completion of the file replacement operation may the Business Logic Layer commit the temporary state as the new active in-memory application state.
- If persistence fails at any stage:
  - The temporary state must be discarded.
  - The original in-memory state must remain unchanged.
  - The previously persisted JSON state must remain unchanged where failure occurs before successful replacement.
  - A `DatabaseWriteException` must be raised.
  - The UI must report the failure without displaying a transaction success confirmation.

This process ensures that the application does not expose an unpersisted financial transaction as a successful operation.

## 6.4 Transaction Guarantee and Failure Boundaries

The application implements a single-file transactional persistence strategy rather than a full database transaction mechanism.

The logical transaction consists of the proposed account balance mutations and corresponding ledger additions, persisted together through one complete JSON state replacement.

**The system guarantees that:**

- The active in-memory application state remains unchanged until successful file replacement.
- The existing JSON file remains intact if serialization or staging-file writing fails before replacement.
- A successful replacement makes the complete new JSON state visible as the active persisted state.
- A failed replacement prevents the proposed in-memory state from being committed.

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
- Once the ledger reaches 10,000 records, the system must reject any new INCOME, EXPENSE, or TRANSFER operation that would increase the count beyond the supported limit.
- Capacity validation must occur before proposed account balance mutations, ledger modifications, or persistence operations.
- Existing in-memory and persisted states must remain unchanged following capacity rejection.
- The user must receive a clear notification explaining that the transaction capacity has been reached and that a persistence architecture reassessment is required.

**Future migration path:**

- Transaction volumes exceeding the supported capacity will require an explicit architecture reassessment.
- SQLite is identified as the preferred migration path because it provides structured queries, indexing, and transactional capabilities.

---

# 7.0 Error Handling

## 7.1 Input and Domain Validation Matrix (Business Logic Layer)

The Business Logic Layer must translate expected low-level Python runtime errors and domain validation failures into explicit custom exceptions.

This ensures that the presentation layer receives predictable error types without exposing unnecessary implementation details.

| Expected Error | Root Cause Context | Trapped Native Exception / Condition | Custom Domain Exception | User-Facing Console Feedback |
| --- | --- | --- | --- | --- |
| Invalid Amount Entry | Non-numeric input, invalid decimal structure, empty input, or excessive precision. | `InvalidOperation`, `ValueError`, or validation failure. | `InvalidAmountError` | "Error: Amount must be a valid positive number with up to 2 decimal places." |
| Malformed Account Name | Empty strings, whitespace, or names outside the 4–20 character range. | Internal string validation failure. | `InvalidAccountNameError` | "Error: Account name cannot be blank and must be between 4 and 20 characters long." |
| Duplicate Account Name | An existing account already has the requested name. | Case-insensitive uniqueness validation failure. | `DuplicateAccountNameError` | "Error: An account with this name already exists." |
| Invalid Account Type | Input does not match an allowed account enum. | Enum membership validation failure. | `InvalidAccountTypeError` | "Error: Invalid account type. Must be CASH, BANK, SAVINGS, or MOBILE\_WALLET." |
| Invalid Account Status | Input does not match ACTIVE or INACTIVE. | Enum membership validation failure. | `InvalidAccountStatusError` | "Error: Account state must be either ACTIVE or INACTIVE." |
| Invalid Transaction Date | Malformed date, invalid calendar date, or future date. | `ValueError` or date validation failure. | `InvalidDateError` | "Error: Invalid transaction date. Use YYYY-MM-DD and ensure the date is not in the future." |
| Invalid Transaction Type | Input does not match an allowed transaction classification. | Enum membership validation failure. | `InvalidTransactionTypeError` | "Error: Transaction type must be INCOME, EXPENSE, or TRANSFER." |
| Invalid Account / Transaction ID | Empty, malformed, or non-existent entity identifier. | Lookup or membership validation failure. | `EntityNotFoundError` | "Error: The requested account or transaction ID does not exist." |
| Invalid Category | Expense category fails the configured category validation rules. | Category membership validation failure. | `InvalidCategoryError` | "Error: Please select a valid expense category." |
| Insufficient Funds | Transaction amount exceeds the available source account balance. | Balance sufficiency validation failure. | `InsufficientFundsError` | "Error: Transaction aborted. Insufficient funds in the selected source account." |
| Self Transfer Violation | Source and target account IDs are identical. | Equality validation failure. | `SelfTransferError` | "Error: Source and destination accounts cannot be the same." |
| Inactive Account Mutation | A transaction references an inactive account. | Account lifecycle validation failure. | `InactiveAccountError` | "Error: Cannot post transactions to or from a deactivated account." |
| Account Balance Not Zero | User attempts to deactivate an account with a non-zero ledger-derived balance. | Balance validation failure. | `AccountBalanceNotZeroError` | "Error: Account cannot be deactivated until its balance reaches zero." |
| Transaction Capacity Exceeded | Historical transaction count has reached 10,000 records. | Application capacity validation failure. | `TransactionCapacityExceededError` | "Error: Transaction capacity reached. A persistence architecture upgrade is required." |

### 7.1.1 Monetary Input Parsing and Conversion

The Business Logic Layer must use Python's `decimal.Decimal` class to parse monetary input and preserve decimal precision during validation and conversion.

The conversion process must follow these steps:

1. Receive the monetary amount as a string from the CLI.
2. Remove leading and trailing whitespace.
3. Validate the input structure and reject unsupported characters or formatting.
4. Parse the validated string using `Decimal()`.
5. Validate that the amount is numeric, finite, positive, and contains no more than two decimal places.
6. Validate that the amount does not exceed the maximum transaction ceiling.
7. Multiply the validated Decimal amount by 100.
8. Convert the result into an integer representing Kobo.
9. Pass the integer Kobo value to the remaining business logic for processing and persistence.

**Illustrative implementation:**

python

```python
import re
from decimal import Decimal, InvalidOperation

def convert_to_kobo(user_input):
    if not isinstance(user_input, str):
        raise InvalidAmountError()

    value = user_input.strip()

    if not re.fullmatch(r"\d+(?:\.\d{1,2})?", value):
        raise InvalidAmountError()

    try:
        amount = Decimal(value)

        if not amount.is_finite() or amount <= 0:
            raise InvalidAmountError()

        if amount > Decimal("99999999.99"):
            raise InvalidAmountError()

        return int(amount * 100)

    except (InvalidOperation, ValueError):
        raise InvalidAmountError()
```

**Example conversion:**

python

```python
convert_to_kobo("250.50")

# Result:
25050
```

The returned value is an integer representing 25,050 Kobo.

This approach ensures that the monetary input is converted into integer Kobo without introducing binary floating-point precision errors.

The original Naira input must not be used for subsequent financial calculations.

## 7.2 Storage and Persistence Exceptions (Data Access Layer)

The Data Access Layer must intercept low-level operating-system and filesystem anomalies, translating them into controlled persistence exceptions or executing defined initialization actions.

| Expected Error | Root Cause Context | Trapped Native Exception | Custom Exception Raised | User-Facing / System Resolution Feedback |
| --- | --- | --- | --- | --- |
| Missing Storage Ledger | Application initialized for the first time, or storage file manually deleted. | `FileNotFoundError` | None (Gracefully Handled) | Automatically create the missing directory and initialize an empty JSON structure: `{"accounts": {}, "transactions": []}`. |
| Corrupted JSON Payload | Manual tampering or incomplete writes have left invalid JSON syntax. | `json.JSONDecodeError` | `DatabaseCorruptedException` | "Fatal Error: The local database file is corrupted and cannot be parsed. Restore from a valid backup." |
| Write Permission Locked | Host operating system has marked the file or directory as read-only, or another filesystem restriction prevents writing. | `PermissionError` or `OSError` | `DatabaseWriteException` | "Error: Disk write access denied. Please check folder write permissions." |

**Additional persistence requirements:**

- The application must not silently replace an existing corrupted ledger with an empty database.
- Missing-file initialization must occur only when the storage file genuinely does not exist.
- A corrupted existing ledger must trigger a controlled failure rather than automatic data destruction.
- Temporary staging files must be handled appropriately following failed persistence attempts.

## 7.3 Top-Level Catch-All Engine

To prevent unexpected Python tracebacks from leaking into the terminal, the main entry point (`main.py`) must wrap the application execution loop inside a global exception-handling boundary.

**Illustrative implementation:**

python

```python
import sys

try:
    # Run interactive console menu loop
    app.run()

except Exception as e:
    print("\n[CRITICAL ERROR] An unexpected system failure occurred.")
    print("Please restart the application. If issues persist, contact support.")

    # In production, the full exception details should
    # be recorded in an application log.

    sys.exit(1)
```

Expected domain and persistence exceptions should be handled at the appropriate application boundaries so that recoverable errors do not unnecessarily terminate the application.

The global catch-all must serve only as a final safety boundary for unexpected failures.

---

# 8.0 Testing Strategy

To guarantee system stability, mathematical integrity, and compliance with the defined business rules, the application must implement a multi-tiered automated testing suite using Python's built-in `unittest` framework.

Test configurations must explicitly address:

- Happy Paths: Valid inputs and successful operations.
- Failure Paths: Invalid data and rejected operations.
- Boundary Edge Cases: Values at or near defined constraints.
- Persistence Integrity: Successful and unsuccessful file operations.
- Cross-Layer Integration: Communication between application tiers.

## 8.1 Unit Testing (Isolated Functional Integrity)

Unit tests must isolate specific business functions and validation mechanisms.

External dependencies, particularly disk operations and date providers, should be mocked where necessary.

| Targeted Module | Strategy | Test Function Identifier | Test Parameters / Inputs | Expected Terminal State / Exception |
| --- | --- | --- | --- | --- |
| Account Creation | Happy Path | `test_create_account_success` | ID generated automatically, name="Polaris Bank", type="BANK" | Account initialized successfully with zero Kobo and ACTIVE status. |
| Account Creation | Failure Path | `test_create_account_name_too_short` | name="Pol", type="BANK" | Raises `InvalidAccountNameError`. |
| Account Creation | Edge Case | `test_create_account_exact_lower_bound` | name="Opay", type="MOBILE\_WALLET" | Account initialized successfully. |
| Account Creation | Failure Path | `test_duplicate_account_name_case_insensitive` | Existing name="Cash"; new name="cash" | Raises `DuplicateAccountNameError`. |
| Monetary Conversion | Happy Path | `test_naira_to_kobo_conversion` | Input="250.50" | Returns integer `25050`. |
| Monetary Conversion | Edge Case | `test_minimum_valid_monetary_amount` | Input="0.01" | Returns integer `1`. |
| Monetary Conversion | Failure Path | `test_excessive_decimal_precision_rejected` | Input="250.555" | Raises `InvalidAmountError`. |
| Monetary Conversion | Failure Path | `test_zero_amount_rejected` | Input="0.00" | Raises `InvalidAmountError`. |
| Monetary Conversion | Failure Path | `test_non_numeric_amount_rejected` | Input="abc" | Raises `InvalidAmountError`. |
| Monetary Conversion | Failure Path | `test_transaction_ceiling_enforced` | Input="100000000.00" | Raises `InvalidAmountError`. |
| Date Validation | Happy Path | `test_today_date_is_accepted` | Transaction date: 2026-11-11; fixed today: 2026-11-11 | Date accepted successfully. |
| Date Validation | Happy Path | `test_past_date_is_accepted` | Transaction date: 2026-11-10; fixed today: 2026-11-11 | Date accepted successfully. |
| Date Validation | Failure Path | `test_future_date_is_rejected` | Transaction date: 2026-11-12; fixed today: 2026-11-11 | Raises `InvalidDateError`. |
| Date Validation | Failure Path | `test_invalid_calendar_date_is_rejected` | Transaction date: 2026-02-30 | Raises `InvalidDateError`. |
| Date Validation | Failure Path | `test_alternative_date_format_is_rejected` | Transaction date: 2026/11/11 | Raises `InvalidDateError`. |
| Balance Calculation | Happy Path | `test_ledger_derived_balance` | Income: 100,000 Kobo; expense: 25,000 Kobo | Returns 75,000 Kobo. |
| Transfer Processing | Happy Path | `test_transfer_preserves_combined_balance` | Source: 100,000 Kobo; transfer: 25,000 Kobo | Source: 75,000 Kobo; destination increases by 25,000 Kobo. |
| Account Lifecycle | Failure Path | `test_nonzero_balance_blocks_deactivation` | Ledger-derived balance: 1 Kobo | Raises `AccountBalanceNotZeroError`. |
| Account Lifecycle | Happy Path | `test_zero_balance_allows_deactivation` | Ledger-derived balance: 0 Kobo | Account status changes to INACTIVE. |
| Transaction Capacity | Failure Path | `test_transaction_limit_blocks_new_entry` | Existing ledger contains 10,000 records; attempt valid income. | Raises `TransactionCapacityExceededError`; no state mutation or disk write occurs. |
| Transaction Capacity | Edge Case | `test_transaction_limit_allows_final_entry` | Existing ledger contains 9,999 records; attempt valid income. | Transaction succeeds; ledger contains exactly 10,000 records. |

## 8.2 Integration Testing (Cross-Layer Subsystem Communication)

Integration tests must evaluate communication between the Business Logic Layer and Data Access Layer, specifically verifying that `wallet_engine.py` correctly updates and retrieves data through `storage.py`.

| Targeted Interaction | Strategy | Test Function Identifier | Scenario Setup / Inputs | Expected Integration Outcome |
| --- | --- | --- | --- | --- |
| Atomic Entry Lifecycle | Happy Path | `test_business_action_triggers_file_flush` | Post a valid INCOME entry through `wallet_engine.py`. | 1\. Temporary application state is created. 2. Proposed account balance is updated. 3. Transaction is appended. 4. `storage.py` writes the complete state using atomic replacement. 5. New state is committed to active memory. |
| Transaction Conflict | Failure Path | `test_balance_check_blocks_file_write` | Attempt an EXPENSE exceeding the account balance. | 1\. Engine detects insufficient funds. 2. Raises `InsufficientFundsError`. 3. Memory remains unchanged. 4. Disk write is bypassed. |
| Persistence Failure | Failure Path | `test_failed_persistence_preserves_memory_state` | Attempt a valid INCOME transaction while simulating a file-write failure. | 1\. `DatabaseWriteException` is raised. 2. Temporary state is discarded. 3. Original in-memory state remains unchanged. 4. Existing JSON file remains unchanged. 5. User receives an error notification. |
| Transfer Atomicity | Happy Path | `test_transfer_updates_both_accounts_atomically` | Execute a valid transfer between two active accounts. | Both account balances and the transfer ledger record are persisted together. |
| Transfer Validation | Failure Path | `test_inactive_destination_blocks_transfer` | Attempt a transfer into an inactive account. | Raises `InactiveAccountError`; neither account nor ledger is modified. |
| Balance Reconciliation | Happy Path | `test_reconciliation_corrects_cached_balance` | Stored balance differs from ledger-derived balance. | Cached balance is corrected and persisted. |

## 8.3 End-to-End Testing (Terminal Simulation Workflow)

End-to-End testing must simulate a user interacting with the complete live CLI menu interface.

**Execution Framework:**

- Tests must use Python's `unittest.mock.patch` utility to inject sequential user inputs.
- Standard input (`sys.stdin`) must be simulated where appropriate.
- Terminal output (`sys.stdout`) must be captured and inspected.
- Tests must verify that the complete user workflow produces the expected output and persisted state.

**Test Case Example:**

A complete end-to-end simulation must:

1. Boot the application and display the main menu.
2. Select the option to create a new account.
3. Supply a valid account name and account type.
4. Verify that the account is created with ACTIVE status and zero Kobo.
5. Select the income-recording option.
6. Supply a valid Naira amount, target account, transaction date, and descriptive label.
7. Verify that the monetary amount is converted into integer Kobo.
8. Verify that the account balance and transaction ledger are updated.
9. Navigate to the account balance view.
10. Verify that the displayed Naira balance matches the ledger-derived balance.
11. Navigate to the transaction history view and verify the recorded transaction.

The test must confirm that the complete user journey produces consistent results across the CLI, Business Logic Layer, and persisted JSON file.

---

# 9.0 Explicit Out-of-Scope Decisions

To ensure a reliable and focused implementation within the project timeline, the following technical capabilities are explicitly designated as out of scope.

No code structures or implementation workflows will be engineered to support these features in the current release.

## 9.1 Identity and Session Security

- **User Authentication and Authorization:** In alignment with ASM-01 (Single-User Execution Environment), the application will not feature registration screens, password hashing, multi-user login gates, or session management.
- **Role-Based Access Control:** Permission hierarchies and user roles are excluded from the current implementation.

## 9.2 Financial and Currency Scope Boundaries

- **Multi-Currency Frameworks:** The system is built exclusively around a single fiat currency: Nigerian Naira (₦).
- Cross-border currency conversions, foreign exchange calculations, and multi-currency ledger balances are excluded.
- **Automated and Recurring Transactions:** The ledger will handle manually recorded transactions only.
- Automated standing orders, recurring bill schedulers, and future salary automation are outside the current scope.

## 9.3 Infrastructure and Deployment Interfaces

- **Web, Mobile, or Graphical Deployment:** The presentation layer is designed exclusively for a localized Python Command-Line Interface.
- Web hosting architectures, RESTful API servers, mobile applications, and graphical user interfaces are excluded.

## 9.4 External Ecosystem Integrations

- **External Open Banking APIs:** The engine operates within a closed local data environment.
- The application will not connect to live banking webhooks, external payment gateways such as Mono, Flutterwave, or Stripe, or real-time card authorization APIs.
- **Artificial Intelligence Modules:** Categorization and financial reports will rely entirely on user input and conventional application logic.
- Predictive budgeting, AI-powered financial advisory systems, and automated expense categorization are excluded.

---

# 10\. Document-Wide Technical Consistency Rules

The following rules consolidate the most important implementation constraints and must be treated as mandatory throughout development.

1. **Monetary storage:** Every monetary amount must be stored as an integer Kobo value.
2. **Monetary input:** User-entered Naira amounts must be parsed using `Decimal`, validated, multiplied by 100, and converted to integer Kobo.
3. **No floating-point calculations:** Python `float` must never be used for monetary calculations, balance storage, or financial aggregation.
4. **Ledger authority:** The transaction ledger is the authoritative source for account balances.
5. **Cached balances:** `acc_bal` is a cached integer Kobo representation and must be reconciled against the ledger.
6. **Transaction integrity:** Every financial operation must update the relevant account balances and transaction ledger as one logical operation.
7. **Persistence integrity:** Proposed application state must be persisted through the staging-file and atomic replacement strategy before being committed to active memory.
8. **Transfer classification:** Transfers must remain separate from standalone income and expense reporting totals.
9. **Account lifecycle:** Inactive accounts must not participate in new financial transactions.
10. **Deactivation validation:** An account can only be deactivated when its ledger-derived balance is exactly zero Kobo.
11. **Date integrity:** Transaction dates must follow the exact YYYY-MM-DD format and must not be future-dated.
12. **Transaction capacity:** The JSON ledger must enforce the maximum supported capacity of 10,000 records.
13. **Layer separation:** The Presentation Layer must not perform financial calculations or access persistence files directly.
14. **Error handling:** Expected validation and persistence failures must be represented through explicit custom exceptions.
15. **Testing:** Financial calculations, monetary conversion, account lifecycle, transfer atomicity, and persistence failures must be covered by automated tests.

These rules take precedence over illustrative examples wherever an example might otherwise appear inconsistent with the formal business requirements.

---

**END OF DOCUMENT**

## A few important implementation notes

There are three decisions worth keeping in mind when you move from this specification into coding:

1. The ledger is the source of truth. Don't calculate an account balance from `acc_bal` and then use that same cached value to validate transactions. Derive the authoritative balance from the ledger first.
2. The Decimal-to-Kobo conversion belongs at the input validation boundary. Once the amount has been converted, the rest of the application should only receive integer Kobo values.
3. The JSON architecture has a defined ceiling. The 10,000-record limit is now an explicit constraint, not an informal performance suggestion.

One additional technical distinction: `os.replace()` provides atomic file replacement, but it is not by itself a guarantee against power-loss data corruption. The revised persistence section makes that limitation explicit.

My recommendation: Treat this as the baseline specification before implementation. The next logical step is to derive the module responsibilities and function signatures from it, starting with `validators.py`, particularly the Decimal-to-integer-Kobo conversion function.