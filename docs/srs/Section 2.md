# 1\. Requirements Interpretation

## 1.1 Accounts

- **Req-1: Account Creation & Metadata**
  - The system must allow users to create multiple concurrent financial accounts.
  - Every account must have a unique system-generated identifier (ID), a user-defined account name, an account type, a creation timestamp, and an account status.
  - Supported account types are `BANK`, `SAVINGS`, `CASH`, and `MOBILE_WALLET`.
  - Every newly created account must have an initial status of `ACTIVE`.
  - Account identifiers must be generated at the service layer, with duplicate checks performed before account creation.
  - Account timestamps and statuses must be assigned internally by the application.
  - Accounts must be created without an assigned or stored balance attribute. Their balances must be derived from associated transaction records.
- **Req-2: Account Retrieval (View & Inspect)**
  - The system must provide a default list view of all active accounts belonging to the user.
  - The system must provide a separate option for retrieving inactive accounts.
  - The system must allow users to inspect individual accounts, displaying their details, current ledger-derived balance, account status, and associated transaction history.
  - Account inspection must remain available regardless of account status.
  - Inactive accounts may have their current ledger-derived balances calculated and displayed during individual account inspection.
  - Inactive account balances must not be included in active account balance totals or aggregate net worth calculations.
  - Historical transaction records associated with inactive accounts must remain accessible.
- **Req-3: Account Modification**
  - The system must allow users to update the name of an existing account.
  - Updated account names must comply with the naming constraints defined in BR-01.
  - Renaming an account must not modify its identifier or historical transaction references.
  - The uniqueness check must exclude the account currently being renamed but include every other account, regardless of status.
- **Req-4: Account Activation/Deactivation**
  - The system must allow users to deactivate an account, changing its status to `INACTIVE` and removing it from the default active accounts list.
  - The system must allow users to reactivate an inactive account, changing its status to `ACTIVE` and restoring it to the default active accounts list.
  - Deactivation is permitted only when the account's ledger-derived balance is exactly zero Kobo.
  - Reactivation must not alter the account's historical transactions or ledger-derived balance.
  - Account status changes must not modify or delete historical transaction records.

## 1.2 Income

- **Req-5: Income Recording (Metadata)**
  - The system must allow users to record income transactions.
  - The system must capture and validate:
    - Transaction amount (positive monetary value).
    - Target financial account.
    - Transaction date (`YYYY-MM-DD`).
    - Optional descriptive label (e.g., Salary).
  - The target account must belong to the user and must be `ACTIVE`.
- **Req-6: Monetary Input Validation and Conversion**
  - All monetary input must be validated before conversion into the system's internal monetary representation.
  - Monetary values must be positive and contain no more than two decimal places.
  - Invalid monetary values must be rejected.
  - Valid monetary values must be converted into integer Kobo by multiplying their decimal representation by 100.
  - Monetary conversion must not involve rounding.
  - Monetary input parsing must use decimal-safe conversion rather than floating-point arithmetic.
  - The system must reject monetary values that exceed the supported monetary range.
  - All persisted transaction amounts must be represented as integer Kobo.
- **Req-7: Transaction Ledger Logging**
  - The system must write every income record to the permanent transaction history.
  - Income records must be classified as `INCOME`.
  - Transaction identifiers must be generated, checked for duplicates, and assigned to transaction records within the Business Logic Layer.
  - The active in-memory state must only be updated after successful persistence.

## 1.3 Expenses

- **Req-8: Expense Recording (Metadata)**
  - The system must allow users to record expense transactions.
  - The system must capture and validate:
    - Transaction amount (positive monetary value).
    - Source financial account.
    - Transaction date (`YYYY-MM-DD`).
    - Expense category selected from the centrally defined expense-category collection.
    - Optional descriptive label (e.g., Groceries).
  - The source account must belong to the user and must be `ACTIVE`.
  - The system must prevent overdrafts in accordance with BR-10.
- **Req-9: Expense Monetary Validation**
  - Expense amounts must comply with the monetary validation and conversion rules defined in Req-6.
  - Expense amounts must be represented internally as integer Kobo.
- **Req-10: Transaction Ledger Logging**
  - The system must write every expense record to the permanent transaction history.
  - Expense records must be classified as `EXPENSE`.
  - The active in-memory state must only be updated after successful persistence.

## 1.4 Transfers

- **Req-11: Transfer Recording (Metadata)**
  - The system must allow users to record internal transfers between their own accounts.
  - The system must capture and validate:
    - Source account (sender).
    - Target account (recipient).
    - Transaction amount (positive monetary value).
    - Transaction date (`YYYY-MM-DD`).
    - Optional descriptive label.
  - The source and target accounts must be distinct entities.
  - Both accounts must belong to the user and must be `ACTIVE`.
  - Transfer amounts must comply with the monetary validation and conversion rules defined in Req-6.
  - The active in-memory state must only be updated after successful persistence.
- **Req-12: Transfer Balance Validation**
  - A transfer must reduce the source account's balance and increase the target account's balance by the same amount.
  - The source account must have sufficient funds to complete the transfer.
  - Transfers must comply with chronological balance validation rules.
  - A transfer must not cause either account's balance to become negative at any point in its transaction history.
- **Req-13: Independent Transaction Classification**
  - The system must classify internal transfers as `TRANSFER` in the transaction history.
  - `TRANSFER` transactions must be excluded from standalone `INCOME` and `EXPENSE` totals.
  - The source and target account references must both be recorded.
  - `TRANSFER` transactions must not contain an expense category.

## 1.5 Transaction History

- **Req-14: Comprehensive Transaction Ledger View**
  - The system must provide a centralized transaction history containing all historical financial activity.
  - Every transaction record must explicitly contain:
    - Unique transaction ID.
    - Classification type (`INCOME`, `EXPENSE`, or `TRANSFER`).
    - Transaction date.
    - Amount in integer Kobo.
    - Relevant account reference(s).
    - Category, mandatory for `EXPENSE` transactions.
    - Optional descriptive label.
  - Transaction identifiers must be generated and duplicate-checked within the Business Logic Layer.
  - Historical transaction records must remain available even when an associated account becomes inactive.
  - Historical transaction records must never be directly edited or deleted through normal application operations.
  - Incorrectly recorded transactions must be financially counteracted through new ordinary transactions rather than modifications or deletions of historical records.
- **Req-15: Transaction History Pagination and Ordering**
  - The system must implement application-level pagination when retrieving transaction history.
  - The default page size must be 25 records.
  - Users must be able to navigate between available transaction history pages through the CLI.
  - Transactions must be sorted in reverse-chronological order (newest first) by transaction date by default.
  - Transactions sharing the same transaction date must be ordered by insertion order, with the most recently inserted transaction appearing first.
  - The system must preserve transaction insertion order as the secondary ordering criterion.
  - Pagination must be applied only after the relevant filtering and sorting operations have been completed.
  - Pagination must produce deterministic results when multiple transactions share the same transaction date.

## 1.6 Search and Filtering

- **Req-16: Compound Filter Engine**
  - The system must support the dynamic combination of multiple filter parameters within a single transaction history request.
  - Supported filtering criteria must include:
    - **Temporal:** Specific dates or inclusive date ranges.
    - **Categorical:** Transaction type (`INCOME`, `EXPENSE`, `TRANSFER`) and expense category.
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

  - The system must calculate and expose the current monetary balance of every account, regardless of account status, when individual account inspection requires it.
  - Account balances must be derived exclusively from the cumulative financial effects of associated transaction records.
  - Income transactions must increase the balance of their associated account.
  - Expense transactions must decrease the balance of their associated account.
  - Transfer transactions must decrease the source account balance and increase the target account balance by the same amount.
  - Account balances must be calculated using integer Kobo.
  - Accounts must not maintain independently stored or cached balance attributes.
  - Inactive account balances may be calculated and displayed individually but must be excluded from active account balance totals and aggregate net worth calculations.
- **Req-19: Total Aggregate Net Worth Display**
  - The system must provide a consolidated dashboard displaying the aggregate net balance across all active accounts.
  - Inactive accounts must be excluded from the aggregate net worth calculation.
- **Req-20: Strict Mathematical Integrity**
  - The system must guarantee that the aggregate balance equals the sum of all individual active account balances.
  - Balance information must update automatically following successful income, expense, and transfer operations.
  - Balance calculations must remain consistent across account inspection, account listings, and dashboard views.
  - Balance calculations must not depend on independently maintained or cached account balance values.

## 1.8 Financial Reports

- **Req-21: Time-Bounded Financial Summary Engine**
  - The system must generate financial summaries bounded by a user-selected start date and end date.
  - Both dates must be inclusive.
  - The start date must not be later than the end date.
- **Req-22: Core Reporting Metrics**
  - For the selected reporting period, the system must calculate:
    - **Total Income:** Sum of all recorded transactions classified as `INCOME`.
    - **Total Expenses:** Sum of all recorded transactions classified as `EXPENSE`.
    - **Net Delta:** Total Income minus Total Expenses.
- **Req-23: Categorical and Entity Breakdown**
  - The report must provide a breakdown of total expenditure grouped by expense category.
  - The report must display individual account activity, including incoming and outgoing funds for each account during the selected period.
  - Account-level activity must include transfers.
  - Only `EXPENSE` transactions may contribute to expense-category breakdowns.
  - Historical account activity must remain reportable even when an associated account becomes inactive.
- **Req-24: Transfer Exclusion Rule**
  - The reporting engine must explicitly exclude `TRANSFER` transactions from Total Income and Total Expenses.
  - Transfers must not artificially inflate or reduce the user's reported income or expenditure.
  - Account-level activity reports must nevertheless include transfers as incoming or outgoing account movements.
  - Inactive accounts must be excluded from current aggregate net worth calculations.
  - Historical financial reports must not discard previously recorded transactions solely because an associated account is now inactive.

## 1.9 Transaction Correction

- **Req-25: Immutable Transaction Correction Through Compensating Transactions**
  - The system must provide a mechanism for counteracting incorrectly recorded financial transactions without directly modifying or deleting historical records.
  - Corrections must be implemented by recording new ordinary transactions that produce the opposite financial effect of the incorrect transaction.
  - Counteracting transactions must retain their ordinary transaction classifications (`INCOME`, `EXPENSE`, or `TRANSFER`).
  - An incorrectly recorded `INCOME` transaction must be counteracted by an `EXPENSE` transaction of an equal amount against the originally credited account.
  - An incorrectly recorded `EXPENSE` transaction must be counteracted by an `INCOME` transaction of an equal amount against the originally debited account.
  - An incorrectly recorded `TRANSFER` transaction must be counteracted by another `TRANSFER` transaction of an equal amount, with the original source and destination accounts exchanged.
  - Counteracting transactions must comply with the same validation, account-reference, monetary, and chronological balance constraints as ordinary transactions.
  - Users must be able to provide a descriptive label explaining the reason for the counteracting transaction.
  - The original transaction must remain unchanged and accessible in transaction history.
  - The counteracting transaction must remain independently identifiable in the historical ledger.
  - After counteracting an incorrect transaction, the user may record a new transaction containing the correct information.
  - Counteracting transactions must be persisted using the established transaction persistence mechanism.
  - If a counteracting transaction violates chronological balance constraints, the system must reject the operation and raise an appropriate business error.
  - No special transaction classification or reversal relationship is required for counteracting transactions.

## 1.10 Chronological Balance Validation

- **Req-26: Historical Balance Integrity**
  - The system must guarantee that an account's balance never becomes negative at any point in its transaction history.
  - Chronological balance validation must consider the financial effects of all transactions associated with the account.
  - Income transactions increase the account balance.
  - Expense transactions decrease the account balance.
  - Transfers decrease the source account balance and increase the target account balance.
  - When a transaction is recorded with a date earlier than existing transactions, the system must validate the resulting chronological balance sequence rather than relying exclusively on the account's current balance.
  - Validation must consider all subsequent transactions affected by the newly recorded transaction.
  - If any resulting chronological balance becomes negative, the transaction must be rejected.
  - Transactions sharing the same transaction date must be evaluated using their insertion order.
  - Chronological balance validation must apply equally to ordinary transactions and compensating transactions.
  - Chronological balance validation must consider all transactions associated with an account, including transactions dated before the account's creation timestamp.
  - Account creation timestamps must not be used to reject otherwise valid backdated transactions.
  - Account existence must be validated against the application's loaded account collection when a transaction is entered.

## 1.11 Transaction Persistence and State Consistency

- **Req-27: Persistence Before State Mutation**
  - Financial transaction operations must be persisted successfully before corresponding active in-memory application state is updated.
  - A failed persistence operation must not result in an inconsistent in-memory financial state.
  - Failed transaction validation must not produce persisted transaction records.
  - Transaction identifiers must be assigned within the Business Logic Layer before transaction persistence.
  - The established transaction persistence mechanism must be used consistently for income, expenses, transfers, and compensating transactions.