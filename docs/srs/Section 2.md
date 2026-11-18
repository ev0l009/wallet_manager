# 1. Requirements Interpretation

## 1.1 Accounts

- **Req-1: Account Creation & Metadata**
  - The system must allow users to create multiple concurrent financial accounts.
  - Every account must have a unique system-generated identifier (ID), a user-defined account name, an account type, a creation timestamp, an initial balance of zero Kobo, and an account status.
  - Supported account types are BANK, SAVINGS, CASH, and MOBILE.
  - Every newly created account must have an initial status of ACTIVE.
  - Account identifiers, timestamps, statuses, and initial balances must be assigned internally by the application.
- **Req-2: Account Retrieval (View & Inspect)**
  - The system must provide a default list view of all active accounts belonging to the user.
  - The system must provide a separate option for retrieving inactive accounts.
  - The system must allow users to inspect individual accounts, displaying their details, current balance, account status, and associated transaction history.
  - Account inspection must remain available regardless of account status.
- **Req-3: Account Modification**
  - The system must allow users to update the name of an existing account.
  - Updated account names must comply with the naming constraints defined in BR-01.
  - Renaming an account must not modify its identifier or historical transaction references.
  - The uniqueness check must exclude the account currently being renamed but include every other account, regardless of status.
- **Req-4: Account Activation/Deactivation**
  - The system must allow users to deactivate an account, changing its status to INACTIVE and removing it from the default active accounts list.
  - The system must allow users to reactivate an inactive account, changing its status to ACTIVE and restoring it to the default active accounts list.
  - Deactivation is permitted only when the account's ledger-derived balance is exactly zero Kobo.
  - Reactivation must not alter the account's historical transactions or balance.
  - Reactivation must verify that the account name does not conflict with another existing account.

## 1.2 Income

- **Req-5: Income Recording (Metadata)**
  - The system must allow users to record income transactions.
  - The system must capture and validate:
    - Transaction amount (positive monetary value).
    - Target financial account.
    - Transaction date (YYYY-MM-DD).
    - Optional descriptive label (e.g., Salary).
- **Req-6: Account Balance Mutation**
  - Upon successfully recording income, the system must increment the balance of the designated target account by the transaction amount.
- **Req-7: Transaction Ledger Logging**
  - The system must write every income record to the permanent transaction history.
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
    - Expense category selected from the centrally defined expense-category collection.
    - Optional descriptive label (e.g., Groceries).
- **Req-9: Account Balance Mutation**
  - Upon successfully recording an expense, the system must decrement the balance of the designated source account by the transaction amount.
  - The system must prevent overdrafts in accordance with BR-10.
- **Req-10: Transaction Ledger Logging**
  - The system must write every expense record to the permanent transaction history.
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
  - The system must classify internal transfers as TRANSFER in the transaction history.
  - TRANSFER transactions must be excluded from standalone INCOME and EXPENSE totals.
  - The source and target account references must both be recorded.
  - TRANSFER transactions must not contain an expense category.
  - The account mutations and corresponding ledger record must be persisted together.

## 1.5 Transaction History

- **Req-14: Comprehensive Transaction Ledger View**
  - The system must provide a centralized transaction history containing all historical financial activity.
  - Every transaction record must explicitly contain:
    - Unique transaction ID.
    - Classification type (INCOME, EXPENSE, TRANSFER, REVERSAL).
    - Transaction date.
    - Amount in integer Kobo.
    - Relevant account reference(s).
    - Category, mandatory for EXPENSE transactions.
    - Optional descriptive label.
    - Optional reference to an original transaction when the record is a REVERSAL.
  - Historical transaction records must remain available even when an associated account becomes inactive.
  - Historical transactions must never be directly edited or deleted through normal application operations.
  - Reversal records must preserve the original transaction and reference it through its unique transaction ID.
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
    - **Categorical:** Transaction type (INCOME, EXPENSE, TRANSFER, REVERSAL) and expense category.
    - **Entity-based:** Associated financial accounts.
    - **Quantitative:** Inclusive minimum and maximum monetary amounts.
  - Multiple active filters must be evaluated together using logical AND conditions.
  - Account-based filtering must consider both source and target account references where applicable.
  - Reversal records must be identifiable through transaction-type filtering and their original transaction references.
- **Req-17: Graceful Empty-State Handling**
  - When a search or compound filter produces zero matching transactions, the Business Logic Layer must return an empty collection rather than raising an exception.
  - The presentation layer must display a clear message: "No matching transactions found."
  - The CLI must provide an option to reset active filters and return to the unfiltered transaction history.

## 1.7 Balances

- **Req-18: Granular Account Balances**
  - The system must calculate and expose the current monetary balance of every individual account.
  - The ledger-derived balance must serve as the authoritative value.
  - Reversal transactions must be included in balance calculations according to their defined inverse financial effects.
- **Req-19: Total Aggregate Net Worth Display**
  - The system must provide a consolidated dashboard displaying the aggregate net balance across all active accounts.
- **Req-20: Strict Mathematical Integrity**
  - The system must guarantee that the aggregate balance equals the sum of all individual active account balances.
  - Balance information must update automatically following successful income, expense, transfer, and reversal operations.
  - Balance changes must remain consistent across account inspection, account listings, and dashboard views.

## 1.8 Financial Reports

- **Req-21: Time-Bounded Financial Summary Engine**
  - The system must generate financial summaries bounded by a user-selected start date and end date.
  - Both dates must be inclusive.
  - The start date must not be later than the end date.
- **Req-22: Core Reporting Metrics**
  - For the selected reporting period, the system must calculate:
    - **Total Income:** Sum of effective transactions classified as INCOME.
    - **Total Expenses:** Sum of effective transactions classified as EXPENSE.
    - **Net Delta:** Total Income minus Total Expenses.
  - Reversed original transactions and their corresponding reversal records must be excluded from ordinary income and expense totals.
- **Req-23: Categorical and Entity Breakdown**
  - The report must provide a breakdown of total expenditure grouped by expense category.
  - The report must display individual account activity, including incoming and outgoing funds for each account during the selected period.
  - Account-level activity must include transfers and reversal movements.
  - Only effective EXPENSE transactions may contribute to expense-category breakdowns.
- **Req-24: Transfer Exclusion Rule**
  - The reporting engine must explicitly exclude TRANSFER transactions from Total Income and Total Expenses.
  - Transfers must not artificially inflate or reduce the user's reported cash flow.
  - Account-level activity reports must nevertheless include transfers as incoming or outgoing account movements.
  - REVERSAL transactions must be reflected in account-level activity but must not independently inflate or reduce ordinary income and expense reporting totals.
  - Original transactions that have been reversed must be excluded from effective income and expense reporting.

## 1.9 Transaction Correction

- **Req-25: Immutable Transaction Correction**
  - The system must provide a mechanism for correcting incorrectly recorded financial transactions without directly modifying or deleting historical records.
  - Corrections must be implemented through compensating REVERSAL transactions.
  - A reversal must reference the original transaction using its unique transaction ID.
  - The reversal amount must equal the original transaction amount.
  - The reversal must produce the exact inverse financial effect of the original transaction.
  - A transaction may be reversed only once.
  - The original transaction must remain unchanged and accessible in transaction history.
  - After reversal, the user may record a new transaction containing the correct information.
  - Reversal creation and corresponding account balance mutations must be persisted atomically.
  - Reversal operations must comply with the transaction capacity and persistence constraints.

- **Reversal and Ledger Integrity Clarification**
  - A reversal must not modify, delete, deactivate, or remove the original transaction from the historical ledger.
  - Both the original transaction and its corresponding reversal must remain independently identifiable and available for historical balance reconstruction.
  - Ledger-derived balance calculations must apply the original transaction's financial effect and the reversal's exact inverse financial effect.
  - The combined financial effect of a successfully reversed transaction and its corresponding reversal must equal zero.
  - The exclusion of reversed original transactions applies to effective income and expense reporting, not to the underlying ledger balance calculation.

---