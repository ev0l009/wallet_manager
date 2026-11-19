# 5\. Architecture and Layout Blueprint

## 5.1 Three-Tier Layer Separation

### Presentation Layer (`ui/`)

- Manages terminal rendering and command-line display.
- Collects synchronous string inputs using Python's `input()` utility.
- Displays validation errors, transaction confirmations, account information, and reports.
- Invokes application operations through `services/`.
- Must not execute financial calculations or access JSON storage files directly.
- Must not contain independent implementations of business validation rules.
- Must catch expected application exceptions at appropriate user-operation boundaries.

### Core Domain Layer (`models/` and `exceptions.py`)

- Has zero outward dependencies and may be imported by `ui/`, `services/`, and `file_manager/`.
- Defines domain entities (`Account`, `Transaction`), enums, and custom application errors (e.g., `StorageWriteError`).
- `Account` represents a financial account, including its identity, name, account type, creation timestamp, and status (with no stored balance).
- `Transaction` represents an immutable financial event, including its identity, classification, amount, account references, date, and optional metadata.
- Entities represent core domain concepts and enforce their own single-record field invariants (including `from_dict()` / `to_dict()` serialization), while cross-entity rules live in `services/`.

### Business Logic Layer (`services/`)

- Implements business workflows and cross-entity domain validation (`_validate_loaded_data()`, `_validate_chronological_balances()`).
- Enforces the single chronological balance rule via `validate_account_timeline(account_id, transactions)`, called by all write operations and delegated to per account during startup by `_validate_chronological_balances()`.
- Evaluates account, transaction, monetary, category, and date constraints.
- Coordinates account creation, renaming, deactivation, and reactivation.
- Coordinates income, expense, transfer, and reversal operations.
- Calculates ledger-derived balances.
- Implements transaction searching, filtering, sorting, pagination, and financial reporting.
- Manages proposed in-memory state changes before persistence.
- Must not perform direct filesystem operations.

### Data Access Layer (`file_manager/`)

- Isolates all disk input/output operations.
- Handles JSON deserialization and serialization (`load_app_data()` and save operations).
- Executes staging-file writes (`.storage.json.tmp` with `flush()` + `os.fsync()`) and atomic replacement (`os.replace()`).
- Validates the structural integrity of loaded JSON data and delegates record reconstruction to `models/` (`from_dict()`).
- Translates filesystem, serialization, and read-side integrity failures into controlled persistence exceptions (`StorageReadError` and `StorageWriteError` defined in `exceptions.py`).
- Must not import or depend on `services/` or `ui/` (imports only `models/` and `exceptions.py`).


### Dependency Direction

The logical dependency direction is:

```text
             USER
              |
              v
      PRESENTATION LAYER
            (ui/)
              |
              v
      BUSINESS LOGIC LAYER       +--------------------+
          (services/) ---------> |  DOMAIN & ERRORS   |

              |                  |   (models/,        |
              v                  |   exceptions.py)   |
      DATA ACCESS LAYER          +--------------------+
        (file_manager/) ------------------^
              |
              v
       LOCAL JSON STORAGE
```

The application entry point (`main.py`) acts as the composition root responsible for connecting the required components.

**Dependency constraints:**

- `models/` and `exceptions.py` form the dependency-free Domain base and may be imported by `ui/`, `services/`, and `file_manager/`.
- `ui/` may import and call `services/` (never `file_manager/` directly).
- `services/` may import and call `file_manager/` (e.g., `load_app_data()` and save operations).
- `file_manager/` implements persistence using `models/` (`from_dict()` / `to_dict()`) and `exceptions.py` without ever importing `services/` or `ui/`.
- `main.py` imports and initializes the concrete application components.
- No layer may bypass these boundaries to access another layer's internal implementation details.


## 5.2 Project Structure

text

```text
wallet_manager/
│
├── main.py                     # Application entry point and composition root
│
├── ui/                         # Presentation Tier
│   ├── __init__.py
│   ├── menu_states.py          # Valid menu states (Enum)
│   ├── menu_machine.py         # State machine and navigation logic
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
│   ├── constants.py 
│   ├── logger.py             # Supported expense categories and constants
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
├── logs/
│   └── .gitkeep
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
- `status`: ACTIVE or INACTIVE.
- `created_at`: Automatically generated creation timestamp.

Account construction must not allow users or external application components to arbitrarily supply an account ID.

**Illustrative construction:**

python

```python
account = Account(
    name="First Bank",
    account_type=AccountType.BANK
)
```

The entity or its factory must internally generate the account ID, timestamp and ACTIVE status.

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
      "status": "ACTIVE",
      "created_at": "2026-11-10T09:30:00"
    },
    "acc_cBg5i": {
      "id": "acc_cBg5i",
      "acc_name": "Savings Acc",
      "acc_type": "SAVINGS",
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