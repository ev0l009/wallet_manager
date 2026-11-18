Here's a concise, professional `README.md` that reflects the SRS without overwhelming the reader with implementation details.

README.md

# Wallet Manager

A lightweight, single-user personal finance management application built with Python. Wallet Manager provides a command-line environment for managing financial accounts, recording transactions, monitoring balances, and generating financial reports.

## Features

- **Account Management:** Create, rename, deactivate, and reactivate financial accounts.
- **Transaction Recording:** Record income, expenses, and internal transfers.
- **Transaction History:** Search, filter, sort, and paginate historical transactions.
- **Transaction Reversals:** Correct incorrectly recorded transactions without modifying historical records.
- **Balance Management:** Calculate and reconcile account balances using the transaction ledger.
- **Financial Reporting:** Generate account summaries and expense-category breakdowns.
- **Persistent Storage:** Store application data locally using structured JSON files.
- **Data Integrity:** Enforce monetary precision, transaction validation, and atomic persistence operations.

## Technology Stack

| Component | Technology |
| --- | --- |
| Programming Language | Python 3.10+ |
| User Interface | Command-Line Interface (CLI) |
| Persistence | JSON flat-file storage |
| Monetary Representation | Integer Kobo |
| Testing Framework | `unittest` |
| Type Checking | `mypy` (recommended) |

## Project Structure

text

```text
wallet_manager/
│
├── main.py
├── ui/
├── models/
├── services/
├── file_manager/
├── exceptions/
├── utils/
├── tests/
├── docs/
├── logs/
│
├── storage.json
└── README.md
```

## Requirements

- Python 3.10 or higher.
- A standard command-line terminal.
- Write permissions for the application directory.

No external database server is required.

## Installation and Setup

1. Clone or download the project repository.
2. Navigate to the project directory.
3. Ensure Python 3.10 or higher is installed.
4. Run the application:

bash

```bash
python main.py
```

The application initializes its local JSON storage file when one does not already exist.

## Monetary and Transaction Rules

- The application supports Nigerian Naira (₦) exclusively.
- One Naira equals 100 Kobo.
- All internal monetary values are stored as integer Kobo.
- Monetary input is validated using Python's `Decimal`.
- Future-dated transactions are rejected.
- New accounts begin with zero balance.
- Account names must be unique, regardless of capitalization.
- Transfers must involve two distinct active accounts.
- Accounts cannot be deactivated while their balances are non-zero.
- Historical transactions cannot be edited or deleted.
- Incorrect transactions must be corrected through reversal entries.
- The transaction ledger supports a maximum of 10,000 historical records.

## Data Persistence

Application state is maintained in `storage.json`.

The persistence mechanism uses:

- JSON serialization and deserialization.
- Structural validation of loaded records.
- Temporary staging-file writes.
- Atomic file replacement using `os.replace()`.

The application is designed for single-user, single-process execution. Concurrent writers and database-level transaction guarantees are not supported.

**Important:** Back up `storage.json` regularly. The application does not currently provide automated backup or disaster recovery functionality.

## Running Tests

Execute the automated test suite using Python's built-in `unittest` framework:

bash

```bash
python -m unittest discover -s tests -v
```

The test suite is designed to cover:

- Domain validation and business rules.
- Account and transaction operations.
- Monetary conversion and balance calculations.
- Transaction reversals.
- Persistence failures and recovery.
- Cross-layer integration.
- End-to-end CLI workflows.

## Known Limitations

- Single-user local execution only.
- CLI interaction exclusively.
- Nigerian Naira as the only supported currency.
- Manual transaction entry.
- JSON-based persistence with a 10,000-record capacity.
- No external banking or payment integrations.
- No automated recurring transactions.
- No multi-process concurrency control.
- No automated backup or advanced disaster recovery.

## Documentation

Additional technical documentation is maintained in:

text

```text
docs/architecture.md
```

The project's Software Requirements Specification (SRS) serves as the primary reference for functional requirements, architectural decisions, business rules, and implementation constraints.

## License

No license has been specified yet.