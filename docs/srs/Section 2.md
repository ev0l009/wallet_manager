Below are the revised Sections 1 and 2. I've incorporated your new decisions, removed the dedicated REVERSAL transaction mechanism, updated account ID generation, removed account-owned balance attributes, and aligned chronological balance validation with your actual implementation.

I've also retained the original requirement numbering wherever practical and removed obsolete reversal-specific rules.

# 1\. Requirements Interpretation

Revised SRS — Section 1: Requirements Interpretation

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
- **Req-3: Account Modification**
  - The system must allow users to update the name of an existing account.
  - Updated account names must comply with the naming constraints defined in BR-01.
  - Renaming an account must not modify its identifier or historical transaction references.
  - The uniqueness check must exclude the account currently being renamed but include every other account, regardless of status.
- **Req-4: Account Activation/Deactivation**
  - The system must allow users to deactivate an account, changing its status to INACTIVE and removing it from the default active accounts list.
  - The system must allow users to reactivate an inactive account, changing its status to ACTIVE and restoring it to the default active accounts list.
  - Deactivation is permitted only when the account's ledger-derived balance is exactly zero Kobo.
  - Reactivation must not alter the account's historical transactions or ledger-derived balance.

## 1.2 Income

- **Req-5: Income Recording (Metadata)**
  - The system must allow users to record income transactions.
  - The system must capture and validate:
    - Transaction amount (positive monetary value).
    - Target financial account.
    - Transaction date (YYYY-MM-DD).
    - Optional descriptive label (e.g., Salary).
- **Req-7: Transaction Ledger Logging**
  - The system must write every income record to the permanent transaction history.
  - Income records must be classified as `INCOME`.
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
  - The system must prevent overdrafts in accordance with BR-10.
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
    - Transaction date (YYYY-MM-DD).
    - Optional descriptive label.
  - The source and target accounts must be distinct entities.
  - The active in-memory state must only be updated after successful persistence.
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
  - Historical transaction records must remain available even when an associated account becomes inactive.
  - Historical transaction records must never be directly edited or deleted through normal application operations.
  - Incorrectly recorded transactions must be financially counteracted through new ordinary transactions rather than modifications or deletions of historical records.
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
  - The system must calculate and expose the current monetary balance of every individual account.
  - Account balances must be derived exclusively from the cumulative financial effects of associated transaction records.
  - Accounts must not maintain independently stored or cached balance attributes.
- **Req-19: Total Aggregate Net Worth Display**
  - The system must provide a consolidated dashboard displaying the aggregate net balance across all active accounts.
- **Req-20: Strict Mathematical Integrity**
  - The system must guarantee that the aggregate balance equals the sum of all individual active account balances.
  - Balance information must update automatically following successful income, expense, and transfer operations.
  - Balance calculations must remain consistent across account inspection, account listings, and dashboard views.

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
- **Req-24: Transfer Exclusion Rule**
  - The reporting engine must explicitly exclude `TRANSFER` transactions from Total Income and Total Expenses.
  - Transfers must not artificially inflate or reduce the user's reported income or expenditure.
  - Account-level activity reports must nevertheless include transfers as incoming or outgoing account movements.

## 1.9 Transaction Correction

- **Req-25: Immutable Transaction Correction Through Compensating Transactions**
  - The system must provide a mechanism for counteracting incorrectly recorded financial transactions without directly modifying or deleting historical records.
  - Corrections must be implemented by recording new ordinary transactions that produce the opposite financial effect of the incorrect transaction.
  - Counteracting transactions must retain their ordinary transaction classifications (`INCOME`, `EXPENSE`, or `TRANSFER`).
  - An incorrectly recorded INCOME transaction must be counteracted by an EXPENSE transaction of an equal amount against the originally credited account.
  - An incorrectly recorded EXPENSE transaction must be counteracted by an INCOME transaction of an equal amount against the originally debited account.
  - An incorrectly recorded TRANSFER transaction must be counteracted by another TRANSFER transaction of an equal amount, with the original source and destination accounts exchanged.
  - Counteracting transactions must comply with the same validation, account-reference, monetary, and chronological balance constraints as ordinary transactions.
  - Users must be able to provide a descriptive label explaining the reason for the counteracting transaction.
  - The original transaction must remain unchanged and accessible in transaction history.
  - The counteracting transaction must remain independently identifiable in the historical ledger.
  - After counteracting an incorrect transaction, the user may record a new transaction containing the correct information.
  - Counteracting transactions must be persisted using the established transaction persistence mechanism.
  - No special transaction classification or reversal relationship is required for counteracting transactions.