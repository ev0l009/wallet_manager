# **7. Error Handling**

## **7.1 Application Exception Hierarchy**

All expected application-level validation, business-rule, entity lookup, data-integrity, and persistence failures must inherit from a common `WalletError` base exception.

This allows the Presentation Layer to catch expected application failures without catching Python's unrestricted `Exception` class during ordinary user operations.

**Recommended exception hierarchy:**

```
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
├── DataIntegrityError
│   └── NegativeBalanceError
│
└── PersistenceError
    ├── StorageReadError
    └── StorageWriteError
```

**Exception ownership and responsibilities:**

- `WalletError` is the common application exception base.
- `ValidationError` represents invalid user-supplied values or input that fails domain validation.
- `BusinessRuleError` represents operations that violate established account, transaction, or financial rules.
- `EntityNotFoundError` represents references to accounts or transactions that do not exist.
- `DataIntegrityError` represents structurally invalid or internally inconsistent persisted application data.
- `NegativeBalanceError` represents a historical ledger validation failure in which an account's running balance becomes negative. It inherits from `DataIntegrityError` and carries the affected account ID, transaction date, and calculated balance.
- `PersistenceError` represents controlled filesystem, JSON-reading, and storage-writing failures.
- `StorageReadError` represents failures reading or parsing the persisted storage file.
- `StorageWriteError` represents failures writing or replacing the persisted storage file.

All expected application exceptions must provide useful messages suitable for controlled presentation-layer feedback.

Exception classes must not introduce dependencies from the Domain Layer or Data Access Layer into the Presentation Layer or Business Logic Layer.

### **7.1.1 Input and Domain Validation Matrix**

The Business Logic Layer must translate expected input-validation and business-rule failures into explicit custom exceptions.

The Data Access Layer must separately translate filesystem and JSON-reading failures into the designated persistence exceptions.

| Expected Error                       | Root Cause Context                                                                                 | Trapped Native Exception / Condition                     | Custom Exception Raised            | User-Facing Console Feedback                                                                |
| ------------------------------------ | -------------------------------------------------------------------------------------------------- | -------------------------------------------------------- | ---------------------------------- | ------------------------------------------------------------------------------------------- |
| Invalid Amount Entry                 | Non-numeric input, invalid decimal structure, empty input, or excessive precision.                 | `InvalidOperation`, `ValueError`, or validation failure. | `InvalidAmountError`               | "Error: Amount must be a valid positive number with up to 2 decimal places."                |
| Malformed Account Name               | Empty strings, whitespace, or names outside the 4–20 character range.                              | Account-name validation failure.                         | `InvalidAccountNameError`          | "Error: Account name cannot be blank and must be between 4 and 20 characters long."         |
| Duplicate Account Name               | An existing account already has the requested name.                                                | Case-insensitive uniqueness validation failure.          | `DuplicateAccountNameError`        | "Error: An account with this name already exists."                                          |
| Invalid Account Type                 | Input does not match an allowed account type.                                                      | Enum membership validation failure.                      | `InvalidAccountTypeError`          | "Error: Invalid account type. Must be CASH, BANK, SAVINGS, or MOBILE_WALLET."               |
| Invalid Account Status               | Persisted status does not match ACTIVE or INACTIVE.                                                | Persisted entity validation failure.                     | `DataIntegrityError`               | "Fatal Error: Stored account data contains an invalid account status."                      |
| Invalid Transaction Date             | Malformed date, invalid calendar date, or future date.                                             | `ValueError` or date validation failure.                 | `InvalidDateError`                 | "Error: Invalid transaction date. Use YYYY-MM-DD and ensure the date is not in the future." |
| Invalid Transaction Type             | Input does not match an allowed transaction classification.                                        | Enum membership validation failure.                      | `InvalidTransactionTypeError`      | "Error: Transaction type must be INCOME, EXPENSE, or TRANSFER."                             |
| Invalid Account / Transaction ID     | Non-existent account or transaction reference.                                                     | Lookup or membership validation failure.                 | `EntityNotFoundError`              | "Error: The requested account or transaction ID does not exist."                            |
| Invalid Category                     | Expense category fails the configured category validation rules.                                   | Category membership validation failure.                  | `InvalidCategoryError`             | "Error: Please select a valid expense category."                                            |
| Insufficient Funds                   | Transaction or chronological balance validation would result in an impermissible negative balance. | Balance sufficiency validation failure.                  | `InsufficientFundsError`           | "Error: Transaction aborted. Insufficient funds in the selected source account."            |
| Self Transfer Violation              | Source and target account IDs are identical.                                                       | Equality validation failure.                             | `SelfTransferError`                | "Error: Source and destination accounts cannot be the same."                                |
| Inactive Account Mutation            | A transaction references an inactive account.                                                      | Account lifecycle validation failure.                    | `InactiveAccountError`             | "Error: Cannot post transactions to or from a deactivated account."                         |
| Account Balance Not Zero             | User attempts to deactivate an account with a non-zero ledger-derived balance.                     | Balance validation failure.                              | `AccountBalanceNotZeroError`       | "Error: Account cannot be deactivated until its balance reaches zero."                      |
| Transaction Capacity Exceeded        | A new transaction would exceed the 10,000-record maximum.                                          | Application capacity validation failure.                 | `TransactionCapacityExceededError` | "Error: Transaction capacity reached. A persistence architecture reassessment is required." |
| Historical Balance Integrity Failure | A persisted account's historical running balance becomes negative during startup validation.       | Chronological ledger validation failure.                 | `NegativeBalanceError`             | "Fatal Error: Stored transaction history violates the account balance integrity rules."     |

`InvalidAccountStatusError` is not required as a separate user-input exception because users do not manually assign account statuses. Invalid statuses discovered in persisted data must be treated as `DataIntegrityError` failures.

Historical integrity failures must prevent application startup. They must not be silently converted into ordinary validation feedback or repaired automatically.

No reversal-related exceptions are required. Transaction corrections are handled through ordinary compensating transactions, as defined in the business rules.

### **7.1.2 Monetary Input Parsing and Conversion**

The Business Logic Layer must use Python's `decimal.Decimal` class to parse monetary input and preserve decimal precision during validation and conversion.

The conversion process must follow these steps:

1. Receive the monetary amount as a string from the CLI.
2. Remove leading and trailing whitespace.
3. Validate the input structure and reject unsupported characters or formatting.
4. Parse the validated string using `Decimal()`.
5. Validate that the amount is numeric, finite, positive, and contains no more than two decimal places.
6. Validate that the amount does not exceed the centralized maximum transaction ceiling.
7. Multiply the validated Decimal amount by 100.
8. Convert the result into an integer representing Kobo.
9. Pass the integer Kobo value to the remaining business logic for processing and persistence.

**Illustrative implementation:**

```
import refrom decimal import Decimal, InvalidOperationfrom utils.constants import MAX_TRANSACTION_AMOUNT_KOBOfrom exceptions.errors import InvalidAmountErrordef convert_to_kobo(user_input: str) -> int:    if not isinstance(user_input, str):        raise InvalidAmountError()    value = user_input.strip()    if not re.fullmatch(r"\d+(?:\.\d{1,2})?", value):        raise InvalidAmountError()    try:        amount = Decimal(value)        if not amount.is_finite() or amount <= 0:            raise InvalidAmountError()        amount_kobo = amount * 100        if amount_kobo > MAX_TRANSACTION_AMOUNT_KOBO:            raise InvalidAmountError()        return int(amount_kobo)    except InvalidOperation:        raise InvalidAmountError() from None
```

**Example conversion:**

```
convert_to_kobo("250.50")# Result:25050
```

The returned value is an integer representing 25,050 Kobo.

The original Naira input must not be used for subsequent financial calculations. All financial calculations and persisted monetary values must use integer Kobo.

## **7.2 Storage and Persistence Exceptions (Data Access Layer)**

The Data Access Layer must intercept low-level operating-system, filesystem, and JSON-reading failures, translating them into controlled persistence exceptions or executing defined initialization actions.

| Expected Error              | Root Cause Context                                                                                           | Trapped Native Exception                  | Custom Exception Raised   | User-Facing / System Resolution Feedback                                                                                      |
| --------------------------- | ------------------------------------------------------------------------------------------------------------ | ----------------------------------------- | ------------------------- | ----------------------------------------------------------------------------------------------------------------------------- |
| Missing Storage Ledger      | Application initialized for the first time and `storage.json` does not exist.                                | `FileNotFoundError`                       | None (Gracefully Handled) | Return an empty `WalletEngineData` state. The storage file is created when the first successful persistence operation occurs. |
| Corrupted JSON Payload      | Manual tampering or invalid JSON syntax.                                                                     | `json.JSONDecodeError`                    | `StorageReadError`        | "Fatal Error: The local storage file contains invalid JSON and cannot be loaded."                                             |
| Storage Read Failure        | File cannot be accessed or read because of filesystem restrictions or operating-system errors.               | `OSError`                                 | `StorageReadError`        | "Fatal Error: Unable to read the local storage file."                                                                         |
| Invalid Persisted Structure | Missing required fields, invalid entity fields, duplicate identifiers, or invalid persisted monetary values. | Controlled structural validation failure. | `DataIntegrityError`      | "Fatal Error: The local storage file contains invalid application data."                                                      |
| Write Permission Failure    | Host operating system or filesystem restrictions prevent writing.                                            | `PermissionError` or `OSError`            | `StorageWriteError`       | "Error: Disk write access denied. Please check folder write permissions."                                                     |
| Staging File Failure        | Temporary file cannot be created, written, flushed, or synchronized.                                         | `OSError`                                 | `StorageWriteError`       | "Error: Unable to prepare the proposed application state for persistence."                                                    |
| Atomic Replacement Failure  | The operating system prevents `os.replace()` from completing.                                                | `OSError`                                 | `StorageWriteError`       | "Error: Unable to commit the proposed application state to storage."                                                          |

**Additional persistence requirements:**

- The application must not silently replace an existing corrupted ledger with an empty application state.
- Missing-file initialization must occur only when `storage.json` genuinely does not exist.
- A corrupted existing ledger must trigger a controlled startup failure rather than automatic data destruction.
- Structural and entity validation failures must raise `DataIntegrityError`, not `StorageReadError`.
- Filesystem and JSON syntax failures must raise `StorageReadError`.
- Failed staging-file operations must not result in the proposed application state being committed to active memory.
- The previous persisted file must remain intact when replacement fails before successful completion.
- The Data Access Layer must not expose raw filesystem or JSON syntax exceptions directly to the Presentation Layer.
- Stale `.storage.json.tmp` files discovered during startup must be handled according to the cleanup procedure defined in Section 6.1.
- Persistence exceptions must preserve the underlying exception as their cause where appropriate, allowing internal diagnostics without exposing implementation details to the user.

## **7.3 Presentation Layer Error Handling**

The Presentation Layer must catch expected application exceptions through their common `WalletError` base class.

Expected errors must be handled at the individual user-operation boundary.

**Illustrative implementation:**

```
from exceptions.errors import WalletErrordef handle_user_operation(operation):    try:        result = operation()        return result    except WalletError as error:        print(f"\nError: {error}")        return None
```

This approach ensures that:

- Expected validation failures do not terminate the interactive application.
- Business-rule violations are presented as controlled feedback.
- Persistence failures are reported without falsely confirming successful operations.
- The user can return to the interactive menu after recoverable failures.
- Unexpected Python runtime errors are not silently treated as ordinary validation failures.

The Presentation Layer must not independently reproduce domain validation rules.

**Operation success feedback:**

- Success confirmations must be displayed only after the Business Logic Layer reports successful completion.
- A failed validation or persistence operation must never produce a success confirmation.
- Operation-specific success messages should remain the responsibility of the relevant Presentation Layer interaction rather than being generated indiscriminately by a generic exception handler.

**Startup failure handling:**

- Expected exceptions raised during persisted-data loading and integrity validation must prevent application startup.
- The application must report a controlled fatal error and terminate rather than entering the interactive menu with invalid or incomplete application state.
- Startup failures must not be treated as recoverable menu-operation failures.

## **7.4 Top-Level Catch-All Engine**

To prevent unexpected Python tracebacks and internal implementation details from being exposed directly in the terminal, the main entry point (`main.py`) must wrap the application execution loop inside a global exception-handling boundary.

The catch-all must serve only as the final safety boundary for unexpected failures.

**Illustrative implementation:**

```
import loggingimport sysdef main():    try:        app.run()    except Exception:        logging.exception(            "Unexpected application failure."        )        print(            "\n[CRITICAL ERROR] An unexpected system "            "failure occurred."        )        print(            "The application must close safely. "            "Please restart it."        )        sys.exit(1)if __name__ == "__main__":    main()
```

**Additional requirements:**

- The application must configure a persistent logging mechanism.
- Full unexpected exception details and tracebacks must be recorded in the application log.
- The terminal must display a generic error message rather than internal implementation details.
- Expected `WalletError` exceptions must be handled at their appropriate operation boundaries.
- Fatal startup exceptions must be reported through a controlled startup failure path and must prevent the application from entering its normal execution loop.
- The global catch-all must not silently swallow unexpected exceptions.
- The application must terminate safely when an unexpected failure compromises normal execution.
- The application must never display a success confirmation for an operation that did not complete successfully.

---