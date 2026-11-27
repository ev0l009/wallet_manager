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

- Every newly created account must receive a unique system-generated identifier.
- Account identifiers must be generated at the service layer.
- The service layer must check generated identifiers against existing account identifiers before proceeding with account creation.
- UUID-based identifiers or another collision-resistant unique ID mechanism may be used.
- The generated identifier must be supplied to the account during construction.
- Every new account must have an initial status of ACTIVE.
- Account timestamps and statuses must be assigned internally by the application.
- Accounts must be created without an assigned or stored balance attribute.
- Account types must strictly map to the following allowed system enums:
  - CASH
  - BANK
  - SAVINGS
  - MOBILE\_WALLET
- Any other account type must be rejected.
- Initial funding must be recorded through a valid INCOME transaction rather than directly assigning a starting balance.

### BR-03: Reference Validation

- The system must reject any transaction referencing a non-existent, malformed, or invalid account ID.
- Account references must be validated against the application's loaded account collection when the transaction is entered.
- An account's creation timestamp must not be used to determine whether it can be referenced by a backdated transaction.
- Transactions may have financial dates earlier than the creation timestamp of their associated accounts.
- Account names must not be treated as substitutes for unique account identifiers during transaction processing.

### BR-04: Active List Isolation

- The standard account directory must exclusively display accounts with ACTIVE status.
- Inactive accounts must remain accessible through a dedicated inactive-account directory.
- Users must be able to inspect inactive accounts and initiate reactivation through the account management interface.
- Inactive accounts must retain their historical transaction associations and ledger-derived balances.
- The system may calculate and display an inactive account's ledger-derived balance during individual account inspection.
- Inactive account balances must not contribute to active account balance totals or aggregate net worth calculations.
- Historical transaction records associated with inactive accounts must remain accessible.

### BR-05: Deactivation and Reactivation Isolation

- An account may transition from ACTIVE to INACTIVE only if its ledger-derived balance is exactly zero Kobo.
- Account balances must be calculated from historical transaction records rather than retrieved from a stored or cached account balance attribute.
- An inactive account must be blocked from participating in new financial transactions.
- This restriction applies to incoming income, outgoing expenses, and internal transfers as either source or target.
- Reactivation must restore the account's ACTIVE status without changing historical ledger records or the account's ledger-derived balance.
- Account deactivation and reactivation must be persisted using the established atomic file replacement mechanism.

## 2.2 Monetary Values and Validation Mechanics

### BR-06.1: Monetary Representation and Precision Integrity

- All monetary values must be internally represented and stored as integers in the smallest currency denomination, Kobo.
- One Nigerian Naira equals 100 Kobo.
- During input processing, valid Naira amounts must be converted into Kobo by multiplying the decimal amount by 100.
- All financial calculations, including account balance calculations, transfers, chronological balance validation, and financial aggregations, must operate exclusively on integer Kobo values.
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
- The integer Kobo value must be used for all subsequent storage, balance calculations, transfers, and financial calculations.
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
- The ceiling must be enforced before any financial state mutation or persistence operation.
- The ceiling serves as a business and input-validation constraint intended to prevent accidental or implausible individual transaction entries.
- The ceiling applies to INCOME, EXPENSE, and TRANSFER transaction amounts.
- The ceiling applies to individual transactions rather than cumulative account balances or aggregate ledger values.
- Account balances and aggregate financial totals may exceed the individual transaction ceiling through multiple valid transactions.

### BR-10: Balance Invariant

#### BR-10.1: Balance Sufficiency (Overdraft Prevention)

- For EXPENSE and TRANSFER operations, the system must verify that the designated source account has a ledger-derived balance equal to or greater than the intended transaction amount.
- If the transaction amount exceeds the available balance:
  - The operation must be aborted.
  - No financial state may be modified.
  - No transaction record may be appended.
  - No persistence operation may be performed.
  - An `InsufficientFundsError` must be raised.

#### BR-10.2: Chronological Balance Invariant

- The system must guarantee that no account has a negative ledger-derived balance at any point in its transaction history.
- The chronological balance invariant must be enforced through `_validate_chronological_balances()`.
- The validation must consider the historical financial effects of transactions associated with each account.
- The validation must ensure that the resulting chronological balance of every account remains greater than or equal to zero Kobo.
- On transaction writes, the candidate ledger must be validated before persistence.
- If the candidate transaction history violates the chronological balance invariant, the operation must be aborted.
- Invalid financial operations must not modify account state or append transaction records.
- During application startup, `_validate_chronological_balances()` must validate the loaded transaction history.
- If historical transactions violate the chronological balance invariant, the application must raise `DataIntegrityError` and halt startup.
- Transactions must be ordered chronologically by transaction date in ascending order during balance validation.
- Transactions sharing the same transaction date must retain their persisted ledger insertion order.
- The same deterministic ordering must be applied during application startup validation and candidate-ledger validation.

### BR-11: Financial State Authority and Balance Consistency

- The transaction ledger shall serve as the sole authoritative source of financial truth for all account balances.
- Account entities must not maintain independently stored or cached balance attributes.
- Account balances must be calculated dynamically from the cumulative financial effects of associated historical transactions.
- Every successful INCOME, EXPENSE, or TRANSFER operation must persist its corresponding transaction record before the active in-memory transaction state is updated.
- The system must guarantee that calculated account balances remain mathematically consistent with the cumulative financial effects of historical transaction records.
- Balance calculations must never depend on an independently maintained account balance value.
- The ledger-derived balance must serve as the authoritative reference during overdraft validation, chronological balance validation, account lifecycle validation, and financial reporting.

#### BR-11.1: Ledger-Derived Balance Calculation

The system must calculate each account's authoritative balance using the cumulative net effect of all associated historical transactions.

The calculation must follow these rules:

- **INCOME:** Add the transaction amount to the target account.
- **EXPENSE:** Subtract the transaction amount from the source account.
- **TRANSFER:** Subtract the transaction amount from the source account and add the same amount to the target account.

The general balance calculation is:

**Calculated Balance = Total Income + Total Transfers In − Total Expenses − Total Transfers Out**

Where:

- Total Income represents all INCOME transactions credited to the account.
- Total Expenses represents all EXPENSE transactions debited from the account.
- Total Transfers In represents TRANSFER transactions received by the account.
- Total Transfers Out represents TRANSFER transactions sent from the account.

Additional rules:

- Newly created accounts must have no assigned or stored balance.
- The ledger-derived balance of a newly created account with no associated transactions must be zero Kobo.
- Initial funding must be recorded through a valid INCOME transaction.
- Inactive accounts must retain their historical transaction associations and ledger-derived balances.
- The calculated balance must serve as the authoritative reference during overdraft validation, chronological balance validation, and account lifecycle validation.
- An account must not be assigned an arbitrary initial balance outside the transaction ledger.
- The system must calculate ledger-derived balances for both ACTIVE and INACTIVE accounts when required for individual account inspection or account lifecycle validation.
- Inactive account balances must be excluded from active account balance totals and aggregate net worth calculations.
- Account status must affect participation in active financial aggregates, not the underlying calculation of the account's historical ledger balance.

### BR-12: Ledger-Based Balance Verification

- The system must validate the loaded historical transaction ledger against the established financial integrity rules.
- Historical balance verification must use the cumulative financial effects of INCOME, EXPENSE, and TRANSFER transactions.
- The validation must detect historical inconsistencies, including violations of the chronological balance invariant.
- Historical transaction records must never be modified or silently corrected during validation.
- Any detected historical financial inconsistency must raise an appropriate data integrity error.

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
  - No application state may be mutated.
  - No transaction may be appended.
  - An explicit `InsufficientFundsError` must be raised.

## 2.4 Date Validation

### BR-17: Date Format and Structural Integrity

- The system must accept transaction dates exclusively in the ISO 8601 calendar date format: `YYYY-MM-DD`.
- The CLI must not require users to provide hours, minutes, seconds, timezone offsets, or timezone indicators.
- Valid date inputs must be parsed using Python's `datetime.date.fromisoformat()` method.
- The system must enforce the exact `YYYY-MM-DD` input structure before parsing.
- Inputs using alternative ISO 8601 representations must be rejected.
- Invalid inputs must raise `InvalidDateError`.

### BR-18: Calendar Consistency Checks

- The system must perform real-calendar validation on all transaction date inputs.
- Non-existent calendar dates, such as `2026-02-30` or `2026-11-31`, must be rejected.
- Only valid calendar dates may proceed to future-date validation and transaction processing.

### BR-19: Future-Date Restriction

- The system must compare each validated transaction date against the current calendar date obtained from the dedicated date provider.
- Any transaction dated later than the current calendar date must be rejected.
- Transactions dated on the current date or any previous valid calendar date must be accepted.
- Date comparisons must use calendar dates rather than timezone-aware timestamps.

## 2.5 Expense Category Rules

### BR-20: Centralized Expense Category Definition

- The application must maintain one centrally defined collection of permitted expense categories.
- The collection must be maintained in `utils/constants.py` and exposed through the appropriate application model or Business Logic Layer interface.
- The supported expense categories are:
  - `food`
  - `bills`
  - `transport`
  - `airtime`
  - `health`
  - `shopping`
  - `entertainment`
  - `others`
- The collection must be treated as application-controlled configuration.
- The UI must obtain available category options from the Business Logic Layer rather than maintaining an independent category list.
- EXPENSE transactions must contain a valid category from the configured collection.
- INCOME and TRANSFER transactions must have `category = None` (null in JSON).
- Invalid expense categories must raise `InvalidCategoryError`.
- Category validation must be performed before proposed application state is mutated or persisted.

## 2.6 Transaction Correction Rules

### BR-21: Correction Through Compensating Transactions

- The system must not provide a dedicated REVERSAL transaction classification.
- Incorrectly recorded transactions must be counteracted through new ordinary transactions.
- INCOME transactions must be counteracted through EXPENSE transactions.
- EXPENSE transactions must be counteracted through INCOME transactions.
- TRANSFER transactions must be counteracted through TRANSFER transactions in the opposite direction.
- Counteracting transactions must retain their ordinary transaction classifications.
- Counteracting transactions must comply with all applicable transaction validation rules.
- The original transaction must remain unchanged and accessible in the historical ledger.
- The counteracting transaction must be recorded as an independent historical transaction.
- The system must not create a special reversal reference or relationship between the original and counteracting transactions.
- Every counteracting transaction must have its own independently assigned transaction date.
- The original transaction date must not be automatically inherited or substituted for the counteracting transaction date.
- Counteracting transactions must follow the ordinary transaction date validation rules.

### BR-22: Counteracting Transaction Financial Effects

- A counteracting transaction must produce the opposite financial effect of the incorrectly recorded transaction.
- Counteracting an INCOME transaction must debit the account originally credited.
- Counteracting an EXPENSE transaction must credit the account originally debited.
- Counteracting a TRANSFER transaction must credit the original source account and debit the original destination account.
- Counteracting transactions must use an amount equal to the original transaction amount when the intention is to annul the original transaction completely.
- The system must validate the resulting proposed account balances before persistence.
- Counteracting an INCOME or TRANSFER transaction must not be permitted if the resulting account balance would become negative.
- If a counteracting transaction violates the chronological balance invariant, the operation must be aborted.
- Both accounts involved in a counteracting transfer must be updated as one atomic logical operation.
- If a counteracting transaction cannot be completed, the original transaction and existing financial state must remain unchanged.
- A counteracting TRANSFER must be represented by one independently persisted transaction record containing both the original destination and original source account references in their exchanged positions.
- The financial effects on both accounts must be applied as one atomic logical ledger operation.
- No independently maintained account balance attributes may be modified.
- If a compensating transaction requires an inactive account to participate, the account must be reactivated before the compensating transaction can be recorded.
- Reactivation must not modify the original transaction or any existing historical ledger records.

### BR-23: Transaction Correction Reporting and Historical Integrity

- The original transaction must remain visible in historical transaction records after being counteracted.
- The counteracting transaction must appear as a separate historical record.
- Both transactions must retain their independent transaction IDs, classifications, dates, amounts, and applicable account references.
- Counteracting transactions must contribute to financial reports according to their ordinary transaction classifications.
- An EXPENSE transaction used to counteract an INCOME transaction must contribute to reported expenses.
- An INCOME transaction used to counteract an EXPENSE transaction must contribute to reported income.
- A TRANSFER transaction used to counteract another TRANSFER transaction must remain excluded from ordinary income and expense reporting.
- Counteracting transactions must not be automatically excluded from ordinary income or expense reporting.
- Users must be able to identify the purpose of a counteracting transaction through its descriptive label.
- A replacement transaction recorded by the user must be treated as a normal independent transaction.
- Counteracting transactions must comply with BR-09 and all applicable transaction validation and persistence constraints.

---