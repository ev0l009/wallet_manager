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

## 2.5 Expense Category Rules # update this whole section

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

• TrxType values: "income", "expense", "transfer", "reversal".
• ExpCatOpts values (in utils/constants.py / models/): "food", "bills", "transport", "airtime", "health", "shopping", "entertainment", "others" (updating the BR-20 list wording from Utilities/Healthcare/Other to Airtime/Health/Others so prose and enum match 1:1).
• Category constraint: TrxType.EXPENSE requires a valid ExpCatOpts value; TrxType.INCOME, TrxType.TRANSFER, and TrxType.REVERSAL must have category = None (null in JSON), raising InvalidCategoryError otherwise.

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

### BR-24: Reversal rules: # update this whole section
- Target eligibility: Only INCOME, EXPENSE, and TRANSFER transactions can be reversed. Reversing a REVERSAL is rejected (DataIntegrityError / domain error), and each original transaction can be reversed at most once (checked via reverses_transaction_id).
- Account & direction rules: A REVERSAL copies amount == original.amount and swaps source_acc_id and target_acc_id from the original transaction (INCOME reversal has source = original.target, target = None; EXPENSE reversal has source = None, target = original.source; TRANSFER reversal has source = original.target, target = original.source).
- Account status & timeline check: Every referenced account (source_acc_id and/or target_acc_id) must be active, and validate_account_timeline() is run on every affected account with the candidate reversal included (rejecting with NegativeBalanceError if reversing an INCOME or TRANSFER would push an account below 0 at any date).


---