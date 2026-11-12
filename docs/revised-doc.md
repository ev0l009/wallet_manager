# Personal Finance Wallet Manager

## Software Requirements Specification (SRS), Business Rules & Technical Architecture

# 1. Requirements Interpretation

## 1.1 Accounts

- **Req-1: Account Creation & Metadata**
  - The system must allow users to create multiple concurrent financial accounts.
  - Every account must have a unique system-generated identifier (ID), a user-defined account name, an account type, a creation timestamp, an initial balance of zero Kobo, and an account status.
  - Supported account types are BANK, SAVINGS, CASH, and MOBILE\_WALLET.
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

---

# 2\. Business Rules

## 2.1 Accounts & Lifecycle Management

### BR-01: Structural Integrity (Naming Constraints)

- Account names must not be empty, null, or consist exclusively of whitespace.
- Account names must contain between 4 and 20 characters, inclusive.
- Account names must be unique per user profile across both ACTIVE and INACTIVE accounts.
- Uniqueness evaluation must be case-insensitive.
- Leading and trailing whitespace must be removed before validation and persistence.
- Duplicate names must be rejected with an appropriate validation error.
- Account renaming must perform uniqueness validation against every other account, excluding the account currently being renamed.
- Account reactivation must perform the same uniqueness validation before changing its status.

### BR-02: Initial State and Typology

- Every newly created account must automatically receive a unique system-generated identifier.
- UUID-based identifiers or another collision-resistant unique ID mechanism may be used.
- Every new account must have an initial status of ACTIVE.
- Every new account must have an initial balance of zero Kobo.
- Account IDs, timestamps, statuses, and initial balances must be generated or assigned internally.
- Account constructors must not accept externally supplied IDs or arbitrary initial balances during normal account creation.
- Account types must strictly map to the following allowed system enums:
  - CASH
  - BANK
  - SAVINGS
  - MOBILE\_WALLET
- Any other account type must be rejected.
- Initial funding must be recorded through a valid INCOME transaction rather than directly assigning a starting balance.

### BR-03: Reference Validation

- The system must reject any transaction referencing a non-existent, malformed, or invalid account ID.
- Account references must be validated against the application’s loaded account collection.
- Account names must not be treated as substitutes for unique account identifiers during transaction processing.

### BR-04: Active List Isolation

- The standard account directory must exclusively display accounts with ACTIVE status.
- Inactive accounts must remain accessible through a dedicated inactive-account directory.
- Users must be able to inspect inactive accounts and initiate reactivation through the account management interface.
- Inactive accounts must retain their historical balances and transaction associations.

### BR-05: Deactivation and Reactivation Isolation

- An account may transition from ACTIVE to INACTIVE only if its ledger-derived balance is exactly zero Kobo.
- The cached `acc_bal` value must not serve as the sole authority for this validation.
- An inactive account must be blocked from participating in new financial transactions.
- This restriction applies to incoming income, outgoing expenses, and internal transfers as either source or target.
- Reactivation must restore the account's ACTIVE status without changing historical ledger records.
- Reactivation must validate the account name against all other existing accounts.
- Account deactivation and reactivation must be persisted using the established atomic file replacement mechanism.

## 2.2 Monetary Values and Validation Mechanics

### BR-06.1: Monetary Representation and Precision Integrity

- All monetary values must be internally represented and stored as integers in the smallest currency denomination, Kobo.
- One Nigerian Naira equals 100 Kobo.
- During input processing, valid Naira amounts must be converted into Kobo by multiplying the decimal amount by 100.
- All financial calculations, including account balance mutations, transfers, reversals, balance reconciliation, and financial aggregations, must operate exclusively on integer Kobo values.
- During data presentation, Kobo values must be converted into Naira and formatted to exactly two decimal places.
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
- The integer Kobo value must be used for all subsequent storage, balance mutations, transfers, reversals, and financial calculations.
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

def convert_to_kobo(user_input: str) -> int:
    if not isinstance(user_input, str):
        raise InvalidAmountError()

    cleaned_input = user_input.strip()

    if not re.fullmatch(r"\d+(?:\.\d{1,2})?", cleaned_input):
        raise InvalidAmountError()

    try:
        amount = Decimal(cleaned_input)

        if not amount.is_finite() or amount <= 0:
            raise InvalidAmountError()

        if amount > Decimal("99999999.99"):
            raise InvalidAmountError()

        return int(amount * 100)

    except InvalidOperation:
        raise InvalidAmountError()
```

The conversion function must return an integer Kobo value or raise `InvalidAmountError`. No financial operation may proceed using the original user-entered monetary string.

### BR-07: Data Type and Range Constraints

- The system must reject transaction amounts containing invalid characters, empty strings, or null values.
- Transaction amounts must be strictly positive.
- Zero and negative monetary values must be rejected.
- Currency symbols, commas, and other unsupported formatting characters must be rejected during input validation.
- Reversal transaction amounts must be positive and must exactly match their original transaction amounts.

### BR-08: Numeric Precision and Scale (Currency Guard)

- The system must accept monetary input containing zero, one, or two decimal places.
- Inputs containing more than two decimal places must be rejected.
- The system must not silently round or truncate invalid monetary input.
- All validated monetary amounts must be converted to integer Kobo before financial calculations begin.
- This rule establishes monetary precision and representation consistency rather than protecting against integer overflow.
- Python integers support arbitrary precision, so ordinary integer overflow is not a realistic concern for this application.

### BR-09: Transaction Ceiling (Business Validation Boundary)

- The system must reject any single transaction exceeding ₦99,999,999.99.
- The maximum corresponding stored transaction amount is 9,999,999,999 Kobo.
- The ceiling must be enforced before any account balance mutation or persistence operation.
- The ceiling serves as a business and input-validation constraint intended to prevent accidental or implausible individual transaction entries.
- The ceiling applies to INCOME, EXPENSE, TRANSFER, and REVERSAL transaction amounts.
- The ceiling applies to individual transactions rather than cumulative account balances or aggregate ledger values.
- Account balances and aggregate financial totals may exceed the individual transaction ceiling through multiple valid transactions.

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
- Every successful INCOME, EXPENSE, TRANSFER, or REVERSAL operation must update the affected account balance and append the corresponding transaction record as a single atomic logical operation.
- The system must guarantee that stored account balances remain mathematically consistent with the cumulative net effect of historical transaction records.
- If a discrepancy is detected between a stored account balance and its ledger-derived balance, the ledger-derived value must take precedence.
- The stored balance must be recalculated and corrected through the established persistence mechanism.
- Balance reconciliation must never modify historical transaction records.

### BR-11.1: Ledger-Derived Balance Calculation

The system must calculate each account's authoritative balance using the cumulative net effect of all associated historical transactions.

The calculation must follow these rules:

- **INCOME:** Add the transaction amount to the target account.
- **EXPENSE:** Subtract the transaction amount from the source account.
- **TRANSFER:** Subtract the transaction amount from the source account and add the same amount to the target account.
- **REVERSAL of INCOME:** Subtract the original income amount from the original target account.
- **REVERSAL of EXPENSE:** Add the original expense amount back to the original source account.
- **REVERSAL of TRANSFER:** Add the original transfer amount back to the original source account and subtract the same amount from the original target account.

A reversal must derive its account references and inverse financial effects from its original transaction. It must not accept independently supplied account references that could produce a different financial effect.

The general balance calculation is:

**Calculated Balance = Total Income + Total Transfers In + Expense Reversals + Transfer Reversals In − Total Expenses − Total Transfers Out − Income Reversals − Transfer Reversals Out**

Where:

- Total Income represents effective INCOME transactions credited to the account.
- Total Expenses represents effective EXPENSE transactions debited from the account.
- Total Transfers In represents TRANSFER transactions received by the account.
- Total Transfers Out represents TRANSFER transactions sent from the account.
- Reversal movements represent the exact inverse effects of their original transactions.

Additional rules:

- Newly created accounts must begin with a balance of zero Kobo.
- Initial funding must be recorded through a valid INCOME transaction.
- Inactive accounts must retain their historical balances and transaction associations.
- The calculated balance must serve as the authoritative reference during balance reconciliation, overdraft validation, and account lifecycle validation.
- An account must not be assigned an arbitrary initial balance outside the transaction ledger.

### BR-12: Balance Reconciliation

- The system must provide an internal reconciliation mechanism capable of recalculating account balances using historical transaction records.
- Reconciliation must account for all INCOME, EXPENSE, TRANSFER, and REVERSAL transactions associated with each account.
- Original transactions that have been reversed must not contribute their original financial effect independently of their reversal.
- The process must identify discrepancies between stored balances and ledger-derived balances.
- Any discrepancy must be corrected using the ledger-derived value.
- Reconciliation corrections must be persisted safely using the atomic replacement strategy.
- Reconciliation must not generate artificial income, expense, transfer, or reversal transactions.

## 2.3 Transfer Mechanics

### BR-13: Self-Transfer Prevention

- The system must reject transfer operations where the unique identifier of the source account matches that of the destination account.
- The validation must be based on account IDs rather than account names.

### BR-14: Multi-Account Lifecycle and Existence Check

- The system must verify the existence of both source and destination accounts.
- The operation must fail if either account ID does not exist in the loaded application state.
- The system must block transfers if either account has INACTIVE status.

### BR-15: Transfer Quantification and Global Constraints

- All transfer amounts must comply with BR-06, BR-07, BR-08, and BR-09.
- Transfer amounts must be stored as integer Kobo.
- The same transaction amount must be debited from the source and credited to the destination.
- TRANSFER transactions must have a null category field.

### BR-16: Asset Sufficiency (Overdraft Enforcement)

- The system must confirm that the source account's ledger-derived balance is greater than or equal to the transfer amount.
- If the source account has insufficient funds:
  - The transaction must be aborted.
  - No database state may be mutated.
  - No transaction may be appended.
  - An explicit `InsufficientFundsError` must be raised.

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

## 2.5 Expense Category Rules

### BR-20: Centralized Expense Category Definition

- The application must maintain one centrally defined collection of permitted expense categories.
- The collection must be maintained in `utils/constants.py`.
- The initial supported categories are:
  - Food
  - Bills
  - Utilities
  - Transport
  - Healthcare
  - Entertainment
  - Shopping
  - Other
- The collection must be treated as application-controlled configuration.
- The UI must obtain available category options from the Business Logic Layer rather than maintaining an independent category list.
- EXPENSE transactions must contain a valid category from the configured collection.
- INCOME, TRANSFER, and REVERSAL transactions must not independently introduce expense categories.
- Invalid expense categories must raise `InvalidCategoryError`.
- Category validation must be performed before proposed application state is mutated or persisted.

## 2.6 Transaction Reversal Rules

### BR-21: Reversal Eligibility and Reference Integrity

- Only existing INCOME, EXPENSE, and TRANSFER transactions may be reversed.
- A REVERSAL transaction must reference exactly one original transaction through `reverses_transaction_id`.
- The referenced transaction must exist in the historical ledger.
- A transaction that has already been reversed must not be reversed again.
- A reversal transaction must not reference another reversal transaction.
- The original transaction and its associated metadata must remain unchanged.

### BR-22: Reversal Financial Effects

- A reversal must exactly negate the financial effect of its original transaction.
- Reversing an INCOME transaction must debit its original target account.
- Reversing an EXPENSE transaction must credit its original source account.
- Reversing a TRANSFER transaction must credit the original source account and debit the original target account.
- Both accounts involved in a transfer reversal must be updated as one atomic logical operation.
- The reversal must use the original transaction's amount and account references.
- The system must validate the resulting proposed balances before persistence.
- A reversal must not be permitted if it would produce an invalid negative account balance.
- If a reversal cannot be completed, the original transaction and all account balances must remain unchanged.

### BR-23: Reversal Reporting and Historical Integrity

- The original transaction must remain visible in historical transaction records.
- The reversal must appear as a separate historical record.
- The original transaction must be marked as reversed through its relationship to the reversal record or through a derived status.
- Reversed original INCOME and EXPENSE transactions must be excluded from effective income and expense reporting.
- REVERSAL transactions must not independently contribute to ordinary income and expense totals.
- The replacement transaction recorded by the user must be treated as a normal independent transaction.
- Reversal records must be included in account-level activity and transaction history.
- Reversal creation must comply with BR-09 and the maximum transaction capacity.

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

### ASM-06: Controlled Application Configuration

- The application assumes that supported account types, transaction classifications, and expense categories are centrally defined.
- Configuration changes must be made through controlled application updates rather than arbitrary user modifications to the JSON storage file.
- Existing historical transaction records must remain readable following compatible configuration updates.

---

# 4\. Identified Ambiguities

### AMB-01: Terminal Interaction Pattern

- **Ambiguity:** The original requirements define functional capabilities but do not specify how users should interact with the application through the CLI.
- **Resolution:** The application will use a synchronous interactive menu loop implemented with Python's native `input()` utility rather than raw command-line argument parsing.

### AMB-02: Structural Casing for Uniqueness Constraints

- **Ambiguity:** The original requirements require unique account names but do not define how capitalization should affect uniqueness.
- **Resolution:** Account-name uniqueness will be evaluated case-insensitively across both active and inactive accounts.
- **Example:** "Cash" and "cash" will be treated as duplicate account names.
- Leading and trailing whitespace will be removed before uniqueness evaluation.
- Renaming and reactivation will enforce the same uniqueness rule.

### AMB-03: Persistence Technology Selection

- **Ambiguity:** The original requirements specify persistent transaction history but do not prescribe a storage technology.
- **Resolution:** The application will use a structured JSON flat-file as its exclusive persistence mechanism. SQLite and other database management systems are excluded from the current implementation.

**Justification:**

JSON provides a lightweight, human-readable persistence mechanism suitable for the application's single-user, single-process execution environment. It integrates directly with Python's native `json` module and supports the established Data Access Layer architecture.

**Trade-off:**

JSON does not provide native database indexing, query optimization, transactional rollback, or database-level concurrency controls. Consequently, large transaction histories will increase file parsing, serialization, filtering, and pagination costs.

### AMB-04: Transaction Category and Description Semantics

- **Ambiguity:** The requirements distinguish descriptive labels from expense categories but do not explicitly define how these fields apply to each transaction type.
- **Resolution:**
  - EXPENSE transactions must contain a category and may contain a descriptive label.
  - INCOME transactions may contain a descriptive label but do not require an expense category.
  - TRANSFER transactions may contain a descriptive label but do not require an expense category.
  - REVERSAL transactions must inherit their financial references from the original transaction and may contain a descriptive correction label.
- The category field must be `null` for INCOME, TRANSFER, and REVERSAL records.
- The category field must not be used to classify internal transfers or reversals.

### AMB-05: Account Balance Initialization

- **Ambiguity:** The original requirements do not define how newly created accounts acquire their initial balances.
- **Resolution:** All accounts must begin with zero Kobo.
- Initial funding must be recorded through a valid INCOME transaction rather than directly assigning a starting balance.
- This preserves the ledger as the authoritative source of account balances.

### AMB-06: Transaction Correction Mechanism

- **Ambiguity:** The original requirements establish an immutable transaction ledger but do not specify how users recover from incorrectly recorded transactions.
- **Resolution:** Historical transactions must never be directly edited or deleted.
- Incorrect transactions must be corrected through compensating REVERSAL transactions.
- The user may subsequently record a replacement transaction containing the correct information.
- Original transactions and their reversals must remain independently identifiable in the historical ledger.

### AMB-07: Architecture Dependency Direction

- **Ambiguity:** The original architecture describes communication between the Business Logic and Data Access Layers without defining dependency ownership.
- **Resolution:** The application will use one-way runtime interaction:
  - Presentation Layer calls the Business Logic Layer.
  - Business Logic Layer uses an abstract storage interface.
  - Data Access Layer implements that interface.
  - The application entry point connects the concrete storage implementation to the Business Logic Layer.
- The Data Access Layer must not import or depend on the Business Logic Layer or Presentation Layer.
- Dependency injection will allow business operations to be tested without physical disk access.

---

# 5\. Architecture and Layout Blueprint

## 5.1 Three-Tier Layer Separation

### Presentation Layer (`ui/`)

- Manages terminal rendering and command-line display.
- Collects synchronous string inputs using Python's `input()` utility.
- Displays validation errors, transaction confirmations, account information, and reports.
- Invokes application operations through the Business Logic Layer.
- Must not execute financial calculations or access JSON storage files directly.
- Must not contain independent implementations of business validation rules.
- Must catch expected application exceptions at appropriate user-operation boundaries.

### Business Logic Layer (`models/` and `services/`)

- Implements business workflows and domain validation.
- Evaluates account, transaction, monetary, category, and date constraints.
- Coordinates account creation, renaming, deactivation, and reactivation.
- Coordinates income, expense, transfer, and reversal operations.
- Calculates ledger-derived balances.
- Implements transaction searching, filtering, sorting, pagination, and financial reporting.
- Manages proposed in-memory state changes before persistence.
- Depends on an abstract storage contract rather than a concrete JSON implementation.
- Must not perform direct filesystem operations.

**Domain entities:**

- `Account` represents a financial account, including its identity, name, account type, creation timestamp, status, and cached balance.
- `Transaction` represents an immutable financial event, including its identity, classification, amount, account references, date, and optional metadata.

These entities represent application data and domain concepts. They are not merely collections of validators.

Validation rules may be implemented through entity methods, dedicated validation functions, or application services depending on their scope.

### Data Access Layer (`file_manager/`)

- Isolates all disk input/output operations.
- Implements the abstract storage interface defined by the Business Logic Layer.
- Handles JSON deserialization and serialization.
- Executes staging-file writes and atomic replacement.
- Validates the structural integrity of loaded persistence data.
- Translates filesystem and serialization failures into controlled persistence exceptions.
- Must not import or depend on Business Logic or Presentation modules.

### Dependency Direction

The logical dependency direction is:

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
       STORAGE INTERFACE
        (storage protocol)
              ^
              |
      DATA ACCESS LAYER
          (storage.py)
              |
              v
       LOCAL JSON STORAGE
```

The concrete storage implementation is injected into the Business Logic Layer during application initialization.

The application entry point (`main.py`) acts as the composition root responsible for connecting the required components.

**Dependency constraints:**

- `ui.py` may import and call `wallet_engine.py`.
- `wallet_engine.py` may depend on the abstract storage interface.
- `storage.py` implements the storage interface without importing the Business Logic Layer.
- `main.py` imports and initializes the concrete application components.
- The Data Access Layer must never call Business Logic operations directly.
- No layer may bypass the established dependency boundaries to access another layer's internal implementation details.

## 5.2 Project Structure

text

```text
wallet_manager/
│
├── main.py                     # Application entry point and composition root
│
├── ui/                         # Presentation Tier
│   ├── __init__.py
│   └── ui.py                   # Menu engine and terminal input collectors
│
├── models/                     # Domain Model
│   ├── __init__.py
│   ├── account.py              # Account domain entity
│   ├── transaction.py          # Transaction domain entity
│   └── enums.py                # Account and transaction enums
│
├── services/                   # Business Logic Tier
│   ├── __init__.py
│   ├── wallet_engine.py        # Main coordinator for core workflows
│   ├── reporting.py            # Financial aggregation and report generation
│   └── query_service.py        # Filtering, searching, sorting, pagination
│
├── file_manager/               # Data Access Tier
│   ├── __init__.py
│   ├── storage.py              # JSON persistence implementation
│   └── storage_interface.py    # Abstract storage contract
│
├── exceptions/                 # Application Exception Hierarchy
│   ├── __init__.py
│   └── errors.py               # Custom domain and persistence exceptions
│
├── utils/                      # Shared Components
│   ├── __init__.py
│   ├── validators.py           # Reusable monetary and date validators
│   ├── constants.py            # Supported expense categories and constants
│   └── date_provider.py        # Injectable date provider
│
├── tests/                      # Automated Testing Suite
│   ├── __init__.py
│   ├── test_models.py
│   ├── test_wallet_engine.py
│   ├── test_reporting.py
│   ├── test_query_service.py
│   ├── test_storage.py
│   └── test_integration.py
│
├── docs/                       # Supporting Documentation
│   └── architecture.md
│
├── README.md                   # Installation and usage documentation
│
└── storage.json                # Local persistent application state
```

**Module responsibilities:**

- `account.py`: Defines the Account entity and account-specific invariants.
- `transaction.py`: Defines the Transaction entity and transaction-specific invariants.
- `enums.py`: Defines supported account statuses, account types, and transaction classifications.
- `wallet_engine.py`: Coordinates application workflows and state transitions.
- `reporting.py`: Calculates financial summaries and account activity reports.
- `query_service.py`: Implements transaction retrieval, filtering, sorting, and pagination.
- `storage_interface.py`: Defines the abstract persistence contract.
- `storage.py`: Implements JSON loading, serialization, and atomic file replacement.
- `errors.py`: Defines the common application exception hierarchy.
- `validators.py`: Implements reusable input and structural validation.
- `constants.py`: Stores centrally defined expense categories and application constants.
- `date_provider.py`: Provides an injectable source of the current calendar date.

## 5.3 Domain Entity Design

### Account Entity

The Account entity must represent a financial account and enforce its structural requirements.

Its properties include:

- `id`: Automatically generated unique account identifier.
- `acc_name`: Validated account name.
- `acc_type`: Supported account type.
- `acc_bal`: Cached integer Kobo balance.
- `status`: ACTIVE or INACTIVE.
- `created_at`: Automatically generated creation timestamp.

Account construction must not allow users or external application components to arbitrarily supply an account ID, initial balance, or status.

**Illustrative construction:**

python

```python
account = Account(
    name="First Bank",
    account_type=AccountType.BANK
)
```

The entity or its factory must internally generate the account ID, timestamp, ACTIVE status, and zero-Kobo balance.

### Transaction Entity

The Transaction entity must represent an immutable historical financial event.

Its properties include:

- `id`: Automatically generated transaction identifier.
- `amount`: Positive integer Kobo value.
- `trx_type`: INCOME, EXPENSE, TRANSFER, or REVERSAL.
- `category`: Optional expense category.
- `desc`: Optional descriptive label.
- `source_acc_id`: Source account reference where applicable.
- `target_acc_id`: Target account reference where applicable.
- `transaction_date`: Validated calendar date.
- `reverses_transaction_id`: Original transaction reference for REVERSAL records.

The transaction entity must not permit direct mutation of historical transaction attributes after creation.

A reversal must derive its original account references and financial effect from the referenced transaction.

## 5.4 Data Structure

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
      "acc_bal": 1050000,
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
      "transaction_date": "2026-11-10",
      "reverses_transaction_id": null
    },
    {
      "id": "trx_1oerf",
      "amount": 1050000,
      "trx_type": "INCOME",
      "category": null,
      "desc": "Initial account funding",
      "source_acc_id": null,
      "target_acc_id": "acc_aBc12",
      "transaction_date": "2026-11-10",
      "reverses_transaction_id": null
    },
    {
      "id": "trx_0q1wS",
      "amount": 500000,
      "trx_type": "TRANSFER",
      "category": null,
      "desc": "Moving to savings",
      "source_acc_id": "acc_aBc12",
      "target_acc_id": "acc_cBg5i",
      "transaction_date": "2026-11-10",
      "reverses_transaction_id": null
    },
    {
      "id": "trx_8kLm2",
      "amount": 25000,
      "trx_type": "REVERSAL",
      "category": null,
      "desc": "Correction of incorrectly recorded expense",
      "source_acc_id": "acc_aBc12",
      "target_acc_id": null,
      "transaction_date": "2026-11-11",
      "reverses_transaction_id": "trx_123Df"
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
- REVERSAL records must reference exactly one original transaction.
- Only EXPENSE records require a non-null category.
- INCOME, TRANSFER, and REVERSAL records must have null categories.
- A transaction must not reference an account that did not exist when the transaction was originally recorded.
- Account balances must be reconciled against the transaction ledger.
- Historical transaction identifiers and references must remain unchanged.

The JSON structure is illustrative. Actual account and transaction identifiers must be generated dynamically rather than copied from the example.

---

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

# 7\. Error Handling

## 7.1 Application Exception Hierarchy

All expected application-level validation, business-rule, entity lookup, and persistence failures must inherit from a common `WalletError` base exception.

This allows the Presentation Layer to catch expected application failures without catching Python's unrestricted `Exception` class.

**Recommended exception hierarchy:**

text

```text
WalletError
│
├── ValidationError
│   ├── InvalidAmountError
│   ├── InvalidDateError
│   ├── InvalidAccountNameError
│   ├── InvalidAccountTypeError
│   ├── InvalidTransactionTypeError
│   └── InvalidCategoryError
│
├── BusinessRuleError
│   ├── DuplicateAccountNameError
│   ├── InsufficientFundsError
│   ├── InactiveAccountError
│   ├── SelfTransferError
│   ├── AccountBalanceNotZeroError
│   └── TransactionCapacityExceededError
│
├── EntityNotFoundError
│
├── TransactionCorrectionError
│   ├── TransactionAlreadyReversedError
│   └── InvalidReversalError
│
└── PersistenceError
    ├── DatabaseWriteException
    └── DatabaseCorruptedException
```

**Exception ownership:**

- `WalletError` is the common application exception base.
- `ValidationError` represents invalid user-supplied values or structurally invalid input.
- `BusinessRuleError` represents operations that violate established financial or account rules.
- `EntityNotFoundError` represents references to missing application entities.
- `TransactionCorrectionError` represents invalid or prohibited reversal operations.
- `PersistenceError` represents controlled storage and filesystem failures.

All expected application exceptions must provide useful messages suitable for controlled presentation-layer feedback.

### 7.1.1 Input and Domain Validation Matrix

The Business Logic Layer must translate expected low-level Python runtime errors and domain validation failures into explicit custom exceptions.

| Expected Error | Root Cause Context | Trapped Native Exception / Condition | Custom Domain Exception | User-Facing Console Feedback |
| --- | --- | --- | --- | --- |
| Invalid Amount Entry | Non-numeric input, invalid decimal structure, empty input, or excessive precision. | `InvalidOperation`, `ValueError`, or validation failure. | `InvalidAmountError` | "Error: Amount must be a valid positive number with up to 2 decimal places." |
| Malformed Account Name | Empty strings, whitespace, or names outside the 4–20 character range. | Internal string validation failure. | `InvalidAccountNameError` | "Error: Account name cannot be blank and must be between 4 and 20 characters long." |
| Duplicate Account Name | An existing account already has the requested name. | Case-insensitive uniqueness validation failure. | `DuplicateAccountNameError` | "Error: An account with this name already exists." |
| Invalid Account Type | Input does not match an allowed account enum. | Enum membership validation failure. | `InvalidAccountTypeError` | "Error: Invalid account type. Must be CASH, BANK, SAVINGS, or MOBILE\_WALLET." |
| Invalid Account Status | Persisted status does not match ACTIVE or INACTIVE. | Data-integrity validation failure. | `DatabaseCorruptedException` | "Error: Stored account data contains an invalid account status." |
| Invalid Transaction Date | Malformed date, invalid calendar date, or future date. | `ValueError` or date validation failure. | `InvalidDateError` | "Error: Invalid transaction date. Use YYYY-MM-DD and ensure the date is not in the future." |
| Invalid Transaction Type | Input does not match an allowed transaction classification. | Enum membership validation failure. | `InvalidTransactionTypeError` | "Error: Transaction type must be INCOME, EXPENSE, TRANSFER, or REVERSAL." |
| Invalid Account / Transaction ID | Non-existent account or transaction reference. | Lookup or membership validation failure. | `EntityNotFoundError` | "Error: The requested account or transaction ID does not exist." |
| Invalid Category | Expense category fails the configured category validation rules. | Category membership validation failure. | `InvalidCategoryError` | "Error: Please select a valid expense category." |
| Insufficient Funds | Transaction amount exceeds the available source account balance. | Balance sufficiency validation failure. | `InsufficientFundsError` | "Error: Transaction aborted. Insufficient funds in the selected source account." |
| Self Transfer Violation | Source and target account IDs are identical. | Equality validation failure. | `SelfTransferError` | "Error: Source and destination accounts cannot be the same." |
| Inactive Account Mutation | A transaction references an inactive account. | Account lifecycle validation failure. | `InactiveAccountError` | "Error: Cannot post transactions to or from a deactivated account." |
| Account Balance Not Zero | User attempts to deactivate an account with a non-zero ledger-derived balance. | Balance validation failure. | `AccountBalanceNotZeroError` | "Error: Account cannot be deactivated until its balance reaches zero." |
| Transaction Capacity Exceeded | Historical transaction count has reached 10,000 records. | Application capacity validation failure. | `TransactionCapacityExceededError` | "Error: Transaction capacity reached. A persistence architecture upgrade is required." |
| Already Reversed Transaction | User attempts to reverse an already reversed transaction. | Reversal eligibility validation failure. | `TransactionAlreadyReversedError` | "Error: This transaction has already been reversed." |
| Invalid Reversal | Referenced transaction is missing, invalid, or cannot be reversed. | Reversal integrity validation failure. | `InvalidReversalError` | "Error: This transaction cannot be reversed." |

`InvalidAccountStatusError` is not required as a user-input exception because users do not manually assign account statuses. Account lifecycle changes must occur through controlled application operations.

Invalid statuses discovered in persisted data must be treated as data-integrity failures.

### 7.1.2 Monetary Input Parsing and Conversion

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

def convert_to_kobo(user_input: str) -> int:
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

    except InvalidOperation:
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

The original Naira input must not be used for subsequent financial calculations.

## 7.2 Storage and Persistence Exceptions (Data Access Layer)

The Data Access Layer must intercept low-level operating-system and filesystem anomalies, translating them into controlled persistence exceptions or executing defined initialization actions.

| Expected Error | Root Cause Context | Trapped Native Exception | Custom Exception Raised | User-Facing / System Resolution Feedback |
| --- | --- | --- | --- | --- |
| Missing Storage Ledger | Application initialized for the first time, or storage file manually deleted. | `FileNotFoundError` | None (Gracefully Handled) | Automatically create the missing directory and initialize an empty JSON structure: `{"accounts": {}, "transactions": []}`. |
| Corrupted JSON Payload | Manual tampering or invalid JSON syntax. | `json.JSONDecodeError` | `DatabaseCorruptedException` | "Fatal Error: The local database file is corrupted and cannot be parsed. Restore from a valid backup." |
| Invalid Persisted Structure | Missing required fields, invalid enums, malformed references, or invalid monetary values. | Controlled structural validation failure. | `DatabaseCorruptedException` | "Fatal Error: The local database contains invalid application data." |
| Write Permission Locked | Host operating system has marked the file or directory as read-only, or another filesystem restriction prevents writing. | `PermissionError` or `OSError` | `DatabaseWriteException` | "Error: Disk write access denied. Please check folder write permissions." |
| Staging File Failure | Temporary file cannot be written, flushed, or completed. | `OSError` | `DatabaseWriteException` | "Error: Unable to prepare the proposed application state for persistence." |
| Atomic Replacement Failure | The operating system prevents `os.replace()` from completing. | `OSError` | `DatabaseWriteException` | "Error: Unable to commit the proposed application state to storage." |

**Additional persistence requirements:**

- The application must not silently replace an existing corrupted ledger with an empty database.
- Missing-file initialization must occur only when the storage file genuinely does not exist.
- A corrupted existing ledger must trigger a controlled failure rather than automatic data destruction.
- Temporary staging files must be handled appropriately following failed persistence attempts.
- The previous persisted file must remain intact when replacement fails.
- The Data Access Layer must not expose raw filesystem exceptions directly to the Presentation Layer.

## 7.3 Presentation Layer Error Handling

The Presentation Layer must catch expected application exceptions through their common `WalletError` base class.

Expected errors must be handled at the individual user-operation boundary.

**Illustrative implementation:**

python

```python
from exceptions.errors import WalletError

def handle_user_operation(operation):
    try:
        result = operation()

        print("Operation completed successfully.")

        return result

    except WalletError as error:
        print(f"\nError: {error}")
        return None
```

This approach ensures that:

- Expected validation failures do not terminate the application.
- Business-rule violations are presented as controlled feedback.
- Persistence failures are reported without falsely confirming successful operations.
- The user can return to the interactive menu after recoverable failures.
- Unexpected Python runtime errors are not silently treated as ordinary validation failures.

The Presentation Layer must not independently reproduce domain validation rules.

## 7.4 Top-Level Catch-All Engine

To prevent unexpected Python tracebacks from leaking into the terminal, the main entry point (`main.py`) must wrap the application execution loop inside a global exception-handling boundary.

The catch-all must serve only as the final safety boundary for unexpected failures.

**Illustrative implementation:**

python

```python
import logging
import sys

def main():
    try:
        app.run()

    except Exception:
        logging.exception(
            "Unexpected application failure."
        )

        print(
            "\n[CRITICAL ERROR] An unexpected system "
            "failure occurred."
        )

        print(
            "The application must close safely. "
            "Please restart it."
        )

        sys.exit(1)


if __name__ == "__main__":
    main()
```

**Additional requirements:**

- The application must configure a persistent logging mechanism.
- Full unexpected exception details and tracebacks must be recorded in the application log.
- The terminal must display a generic error message rather than internal implementation details.
- Expected `WalletError` exceptions must be handled at their appropriate operation boundaries.
- The global catch-all must not silently swallow unexpected exceptions.
- The application must terminate safely when an unexpected failure compromises normal execution.
- The application must never display a success confirmation for an operation that did not complete successfully.

---

# 8.0 Testing Strategy

To guarantee system stability, mathematical integrity, and compliance with the defined business rules, the application must implement a multi-tiered automated testing suite using Python's built-in `unittest` framework.

Testing must cover:

- **Happy Paths:** Valid inputs and successful operations.
- **Failure Paths:** Invalid data and rejected operations.
- **Boundary Edge Cases:** Values at or near defined constraints.
- **Domain Invariants:** Mathematical and structural properties that must always remain true.
- **Persistence Integrity:** Successful and unsuccessful file operations.
- **Restart Persistence:** Recovery of previously committed state after application reinitialization.
- **Cross-Layer Integration:** Communication between application tiers.
- **End-to-End Workflows:** Complete user interactions through the CLI.

## 8.1 Unit Testing (Isolated Functional Integrity)

Unit tests must isolate specific business functions and validation mechanisms.

External dependencies, particularly physical disk operations and date providers, must be replaced with controlled test doubles where appropriate.

The Business Logic Layer must depend on an abstract storage interface so that unit tests can use an in-memory fake storage implementation.

Unit tests must not require access to the actual JSON storage file.

**Example unit test coverage:**

| Targeted Module | Strategy | Test Function Identifier | Test Parameters / Inputs | Expected Terminal State / Exception |
| --- | --- | --- | --- | --- |
| Account Creation | Happy Path | `test_create_account_success` | name="Polaris Bank", type="BANK" | Account receives an automatically generated ID, zero Kobo, and ACTIVE status. |
| Account Creation | Failure Path | `test_create_account_name_too_short` | name="Pol", type="BANK" | Raises `InvalidAccountNameError`. |
| Account Creation | Edge Case | `test_create_account_exact_lower_bound` | name="Opay", type="MOBILE\_WALLET" | Account initialized successfully. |
| Account Creation | Failure Path | `test_duplicate_account_name_case_insensitive` | Existing name="Cash"; new name="cash" | Raises `DuplicateAccountNameError`. |
| Account Creation | Failure Path | `test_duplicate_name_inactive_account` | Existing inactive account name="Cash"; new name="Cash" | Raises `DuplicateAccountNameError`. |
| Account Creation | Happy Path | `test_account_constructor_generates_id` | name="First Bank", type="BANK" | ID is generated internally. |
| Account Creation | Happy Path | `test_new_account_starts_with_zero_balance` | Valid account creation. | Initial balance equals zero Kobo. |
| Account Lifecycle | Happy Path | `test_rename_account_success` | Rename existing account to an unused valid name. | Name updated without changing account ID or historical references. |
| Account Lifecycle | Failure Path | `test_rename_account_duplicate_name` | Rename account to another existing account's name. | Raises `DuplicateAccountNameError`. |
| Account Lifecycle | Failure Path | `test_reactivation_duplicate_name` | Reactivate an inactive account whose name conflicts with another account. | Raises `DuplicateAccountNameError`. |
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
| Balance Calculation | Invariant | `test_balance_matches_ledger_sum` | Multiple income, expense, transfer, and reversal records. | Calculated balance matches the cumulative ledger effect. |
| Balance Calculation | Invariant | `test_total_balance_matches_active_accounts` | Multiple active and inactive accounts. | Dashboard total equals the sum of active account balances only. |
| Transfer Processing | Happy Path | `test_transfer_preserves_combined_balance` | Source: 100,000 Kobo; transfer: 25,000 Kobo. | Source decreases by 25,000 Kobo and destination increases by 25,000 Kobo. |
| Transfer Processing | Invariant | `test_transfer_preserves_global_balance` | Multiple accounts and valid transfer. | Aggregate balance remains unchanged. |
| Account Lifecycle | Failure Path | `test_nonzero_balance_blocks_deactivation` | Ledger-derived balance: 1 Kobo. | Raises `AccountBalanceNotZeroError`. |
| Account Lifecycle | Happy Path | `test_zero_balance_allows_deactivation` | Ledger-derived balance: 0 Kobo. | Account status changes to INACTIVE. |
| Category Validation | Failure Path | `test_invalid_expense_category` | Category="Unconfigured Category". | Raises `InvalidCategoryError`. |
| Category Reporting | Invariant | `test_transfers_excluded_from_expense_breakdown` | Expense and transfer records. | Only effective expenses contribute to category totals. |
| Transaction Reversal | Happy Path | `test_reverse_income_transaction` | Existing income transaction. | Original target account is debited by the original amount. |
| Transaction Reversal | Happy Path | `test_reverse_expense_transaction` | Existing expense transaction. | Original source account receives the reversed amount. |
| Transaction Reversal | Happy Path | `test_reverse_transfer_transaction` | Existing transfer transaction. | Both original account movements are reversed correctly. |
| Transaction Reversal | Failure Path | `test_transaction_cannot_be_reversed_twice` | Already reversed transaction. | Raises `TransactionAlreadyReversedError`. |
| Transaction Reversal | Invariant | `test_original_transaction_remains_immutable` | Original transaction followed by reversal. | Original transaction attributes remain unchanged. |
| Transaction Reversal | Invariant | `test_reversal_restores_original_balance` | Valid original transaction and reversal. | Original account balances are restored, subject to subsequent transactions. |
| Transaction Capacity | Failure Path | `test_transaction_limit_blocks_new_entry` | Existing ledger contains 10,000 records. | Raises `TransactionCapacityExceededError`; no state mutation. |
| Transaction Capacity | Edge Case | `test_transaction_limit_allows_final_entry` | Existing ledger contains 9,999 records. | Transaction succeeds; ledger contains exactly 10,000 records. |

## 8.2 Integration Testing (Cross-Layer Subsystem Communication)

Integration tests must evaluate communication between the Business Logic Layer and Data Access Layer, specifically verifying that `wallet_engine.py` correctly updates and retrieves data through the storage implementation.

Unlike unit tests, these tests may use temporary physical storage files to verify actual JSON serialization and persistence behaviour.

| Targeted Interaction | Strategy | Test Function Identifier | Scenario Setup / Inputs | Expected Integration Outcome |
| --- | --- | --- | --- | --- |
| Atomic Entry Lifecycle | Happy Path | `test_business_action_triggers_file_flush` | Post a valid INCOME entry through `wallet_engine.py`. | Proposed state is persisted using atomic replacement before being committed to active memory. |
| Transaction Conflict | Failure Path | `test_balance_check_blocks_file_write` | Attempt an EXPENSE exceeding the account balance. | Raises `InsufficientFundsError`; no memory mutation or disk write occurs. |
| Persistence Failure | Failure Path | `test_failed_persistence_preserves_memory_state` | Attempt valid income while simulating a staging-file write failure. | `DatabaseWriteException` is raised; original memory and disk states remain unchanged. |
| Atomic Replacement Failure | Failure Path | `test_replace_failure_preserves_previous_file` | Simulate an `os.replace()` failure. | Proposed state is discarded; existing persisted file remains unchanged. |
| Transfer Atomicity | Happy Path | `test_transfer_updates_both_accounts_atomically` | Execute a valid transfer between two active accounts. | Both account balances and the transfer ledger record are persisted together. |
| Transfer Validation | Failure Path | `test_inactive_destination_blocks_transfer` | Attempt a transfer into an inactive account. | Raises `InactiveAccountError`; neither account nor ledger is modified. |
| Balance Reconciliation | Happy Path | `test_reconciliation_corrects_cached_balance` | Stored balance differs from ledger-derived balance. | Cached balance is corrected and persisted. |
| Reversal Persistence | Happy Path | `test_reversal_persists_original_and_reversal` | Reverse an existing transaction. | Original record remains unchanged and reversal record is persisted atomically. |
| Category Reporting | Happy Path | `test_expense_categories_loaded_correctly` | Retrieve expense category configuration. | Business Logic Layer uses the centrally defined category collection. |

## 8.3 Persistence and Restart Testing

The system must explicitly verify that committed application state survives a complete application reinitialization.

Restart testing must not simply reload data into the existing application object.

A fresh storage instance and Business Logic instance must be created to simulate a genuine application restart.

**Required scenarios:**

### Successful Restart Recovery

1. Initialize the application using a temporary JSON storage file.
2. Create an account.
3. Record an income transaction.
4. Close or discard the current application instance.
5. Create a new storage instance.
6. Create a new Business Logic instance using the new storage instance.
7. Load the persisted JSON state.
8. Verify that the account, transaction, and ledger-derived balance are correctly recovered.

**Expected outcome:**

The new application instance must reconstruct the same committed financial state as the previous instance.

### Failed Write Recovery

1. Initialize the application using a temporary JSON storage file.
2. Record a valid transaction.
3. Simulate a staging-file write failure during a subsequent transaction.
4. Verify that the previous JSON file remains unchanged.
5. Verify that the active in-memory state remains unchanged.
6. Create a fresh application instance.
7. Reload the JSON file.
8. Verify that only the previously committed transactions are present.

### Failed Atomic Replacement Recovery

1. Initialize the application with an existing valid JSON file.
2. Prepare a valid proposed state change.
3. Simulate an `os.replace()` failure.
4. Verify that the previous persisted file remains unchanged.
5. Verify that the proposed in-memory state is discarded.
6. Reload the file using a fresh application instance.
7. Verify that the previously committed state is recovered correctly.

## 8.4 End-to-End Testing (Terminal Simulation Workflow)

End-to-End testing must simulate a user interacting with the complete live CLI menu interface.

**Execution Framework:**

- Tests must use Python's `unittest.mock.patch` utility to inject sequential user inputs.
- Standard input (`sys.stdin`) must be simulated where appropriate.
- Terminal output (`sys.stdout`) must be captured and inspected.
- Tests must verify that complete user workflows produce the expected output and persisted state.

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
11. Navigate to transaction history and verify the recorded transaction.
12. Record an expense.
13. Verify that the expense appears under the correct category.
14. Execute a transfer between two active accounts.
15. Verify that the combined balance remains unchanged.
16. Reverse an incorrectly recorded transaction.
17. Verify that the original transaction remains visible and the reversal is recorded separately.
18. Navigate to the financial reporting interface.
19. Verify that reversed transactions do not distort effective income and expense totals.

The test must confirm that the complete user journey produces consistent results across the CLI, Business Logic Layer, and persisted JSON file.

## 8.5 Domain Invariant Testing

In addition to individual test cases, the application must test the following properties across relevant financial workflows.

### Invariant 1: Ledger Balance Consistency

For every account:

**Cached Account Balance = Ledger-Derived Account Balance**

The equality must hold after every successfully committed financial operation.

### Invariant 2: Aggregate Balance Consistency

**Total Active Account Balance = Sum of All Active Account Balances**

Inactive accounts must be excluded from the active dashboard total.

### Invariant 3: Transfer Conservation

For every valid transfer:

**Source Debit = Destination Credit**

The aggregate balance across all accounts must remain unchanged.

### Invariant 4: Reversal Conservation

For every successfully reversed transaction:

**Original Financial Effect + Reversal Financial Effect = Zero**

This must hold across all accounts affected by the original transaction.

### Invariant 5: Ledger Immutability

A successful reversal must never alter the original transaction's stored attributes.

### Invariant 6: Persistence Consistency

**Committed In-Memory State = Persisted JSON State**

Following every successful operation, the active application state must correspond to the newly persisted JSON state.

Following a failed persistence operation, the original in-memory and persisted states must remain unchanged.

### Invariant 7: Category Reporting Integrity

Only effective EXPENSE transactions may contribute to expense-category breakdowns.

TRANSFERS and REVERSALS must not be treated as ordinary expenses.

---

# 9.0 Typing Strategy

The application must adopt a consistent Python type annotation strategy to improve code readability, maintainability, and early detection of implementation errors.

## 9.1 General Typing Requirements

- All public functions and methods must declare parameter types and return types.
- Internal helper functions should also use type annotations where they improve clarity.
- Domain entities must use explicit field annotations.
- Collections must use appropriate generic types.
- Monetary values must be explicitly represented as integers in Kobo.
- Functions returning no meaningful value must use `None` as their return annotation.
- Unrestricted `Any` types should be avoided unless necessary.
- Optional values must be explicitly represented using appropriate optional or union types.

## 9.2 Domain Model Typing

- Account types, account statuses, and transaction classifications must use Python `Enum` or `StrEnum` where appropriate.
- Domain entities should use Python `dataclasses` where suitable.
- Transaction entities should be immutable after creation.
- Account entities may support controlled state changes through validated domain operations.
- IDs must be represented consistently as strings.
- Transaction dates must use `datetime.date` internally after successful validation.
- Account creation timestamps must use `datetime.datetime`.

## 9.3 Monetary Typing

- All internal monetary amounts must use Python `int` values representing Kobo.
- `Decimal` must be used only during Naira input parsing and conversion.
- Financial calculations must not use Python `float`.
- Functions performing balance calculations must return integer Kobo values.
- Type annotations and documentation must explicitly identify monetary integers as Kobo rather than Naira.

## 9.4 Storage Interface Typing

- The storage contract must use Python's `Protocol` or another suitable abstraction mechanism.
- The Business Logic Layer must depend on the storage contract rather than the concrete JSON storage implementation.
- The concrete Data Access Layer must satisfy the storage contract.
- The storage interface must support dependency injection and substitution with in-memory test doubles.

**Illustrative interface:**

python

```python
from typing import Protocol

class StorageProtocol(Protocol):

    def load_state(self) -> dict:
        ...

    def save_state(self, state: dict) -> None:
        ...
```

The actual implementation may use more specific domain types or typed state structures as the application develops.

## 9.5 Type Checking Expectations

- The project should use a static type checker such as `mypy` during development.
- Type-checking errors involving public interfaces and domain entities must be resolved before release.
- Type annotations must remain consistent across module boundaries.
- Changes to domain models or storage interfaces must be reflected in dependent modules and tests.

---

# 10.0 Documentation Approach

The application must maintain a lightweight but consistent documentation structure covering installation, usage, architecture, and implementation decisions.

## 10.1 README Documentation

The root `README.md` must provide:

- Project overview and objectives.
- Core application features.
- Python version requirements.
- Installation and setup instructions.
- Application execution instructions.
- CLI usage guidance.
- Supported account types and expense categories.
- Important monetary and transaction constraints.
- Testing instructions.
- Known limitations and out-of-scope capabilities.

The README must serve as the primary entry point for developers and users.

## 10.2 Inline Documentation and Docstrings

- Each major module must include a module-level docstring explaining its responsibility.
- Public classes and methods must include docstrings describing their purpose.
- Functions with non-obvious parameters or return values must document their expected inputs and outputs.
- Functions that raise application-specific exceptions must document the relevant exceptions.
- Complex financial calculations must include concise explanations of their mathematical behaviour.
- Comments should explain non-obvious implementation decisions rather than repeat the code.

## 10.3 Architecture Documentation

The `docs/architecture.md` file must document:

- Three-tier architecture responsibilities.
- Dependency direction and dependency injection.
- Domain entity responsibilities.
- Storage interface and JSON persistence implementation.
- Atomic file replacement strategy.
- Ledger-derived balance calculations.
- Transaction reversal behaviour.
- Application exception hierarchy.
- Testing boundaries and expected coverage.

## 10.4 Business Rule Traceability

- Important implementation decisions should reference their corresponding requirement or business rule identifiers.
- Changes to business rules must be reflected in the relevant implementation documentation.
- Documentation must remain consistent with the current application behaviour.
- Outdated examples and descriptions must be updated when their underlying requirements change.

## 10.5 Documentation Maintenance

Documentation must be maintained alongside implementation changes.

A feature must not be considered fully documented if its relevant requirements, business rules, or usage instructions have become inconsistent with its actual behaviour.

---

# 11.0 Explicit Out-of-Scope Decisions

To ensure a reliable and focused implementation within the project timeline, the following technical capabilities are explicitly designated as out of scope.

No code structures or implementation workflows will be engineered to support these features in the current release unless a future requirement formally introduces them.

## 11.1 Identity and Session Security

- **User Authentication and Authorization:** In alignment with ASM-01 (Single-User Execution Environment), the application will not feature registration screens, password hashing, multi-user login gates, or session management.
- **Role-Based Access Control:** Permission hierarchies and user roles are excluded from the current implementation.

## 11.2 Financial and Currency Scope Boundaries

- **Multi-Currency Frameworks:** The system is built exclusively around a single fiat currency: Nigerian Naira (₦).
- Cross-border currency conversions, foreign exchange calculations, and multi-currency ledger balances are excluded.
- **Automated and Recurring Transactions:** The ledger will handle manually recorded transactions only.
- Automated standing orders, recurring bill schedulers, and future salary automation are outside the current scope.

## 11.3 Infrastructure and Deployment Interfaces

- **Web, Mobile, or Graphical Deployment:** The presentation layer is designed exclusively for a localized Python Command-Line Interface.
- Web hosting architectures, RESTful API servers, mobile applications, and graphical user interfaces are excluded.

## 11.4 External Ecosystem Integrations

- **External Open Banking APIs:** The engine operates within a closed local data environment.
- The application will not connect to live banking webhooks, external payment gateways such as Mono, Flutterwave, or Stripe, or real-time card authorization APIs.
- **Artificial Intelligence Modules:** Categorization and financial reports will rely entirely on user input and conventional application logic.
- Predictive budgeting, AI-powered financial advisory systems, and automated expense categorization are excluded.

## 11.5 Advanced Persistence and Concurrency

- **Database Management Systems:** SQLite, PostgreSQL, and other database management systems are excluded from the current implementation.
- **Multi-Process Concurrency:** Concurrent writers and multi-process file synchronization are outside the supported execution model.
- **Advanced Disaster Recovery:** Automated backup scheduling, point-in-time recovery, and distributed replication are excluded.
- The current architecture relies on the documented JSON persistence and atomic replacement strategy.

---

# 12.0 Document-Wide Technical Consistency Rules

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
11. **Account uniqueness:** Account names must be unique across both active and inactive accounts, using case-insensitive comparison.
12. **Account identification:** Account IDs must be generated internally and must remain stable throughout the account's lifetime.
13. **Initial account balance:** Every new account must begin with zero Kobo. Initial funding must be recorded through a valid INCOME transaction.
14. **Date integrity:** Transaction dates must follow the exact YYYY-MM-DD format and must not be future-dated.
15. **Expense categories:** Permitted expense categories must be centrally defined and validated through the Business Logic Layer.
16. **Transaction immutability:** Historical transaction records must never be directly edited or deleted.
17. **Transaction correction:** Incorrect financial transactions must be corrected through compensating REVERSAL transactions.
18. **Reversal integrity:** A transaction may be reversed only once, and every reversal must reference its original transaction.
19. **Reporting integrity:** Reversed original transactions and their corresponding reversals must not distort ordinary income and expense totals.
20. **Transaction capacity:** The JSON ledger must enforce the maximum supported capacity of 10,000 historical transaction records.
21. **Layer separation:** The Presentation Layer must not perform financial calculations or access persistence files directly.
22. **Dependency direction:** The UI depends on the Business Logic Layer, while the Business Logic Layer depends on an abstract storage contract implemented by the Data Access Layer.
23. **Storage isolation:** The Data Access Layer must not import or depend on Business Logic or Presentation modules.
24. **Error handling:** Expected validation, business-rule, and persistence failures must be represented through the common `WalletError` exception hierarchy.
25. **UI error handling:** The Presentation Layer must catch expected application exceptions at appropriate user-operation boundaries.
26. **Unexpected failures:** The top-level application boundary must log unexpected exceptions and terminate safely.
27. **Testing isolation:** Business Logic unit tests must use injected in-memory storage implementations rather than physical disk operations.
28. **Persistence testing:** Integration tests must verify successful persistence, staging-file failures, atomic replacement failures, and recovery after a fresh application restart.
29. **Mathematical integrity:** Account balances must reconcile with the cumulative financial effects of the complete transaction ledger, including reversals.
30. **Typing:** Public functions, domain entities, and cross-layer interfaces must use consistent Python type annotations.
31. **Documentation:** Implementation documentation must remain aligned with the requirements, business rules, and actual application behaviour.

These rules take precedence over illustrative examples wherever an example might otherwise appear inconsistent with the formal business requirements.

---

**END OF DOCUMENT**