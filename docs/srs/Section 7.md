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