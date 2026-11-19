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