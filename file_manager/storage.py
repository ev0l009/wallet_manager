"""Data persistence layer for the Wallet Manager application.

Handles JSON serialization and deserialization of application data.
Delegates entity reconstruction to the domain models and uses atomic
file replacement when saving application state.
"""

import json
import os
from pathlib import Path

from models.account import Account
from models.transaction import Transaction
from models.types import JSONData, WalletEngineData

from exceptions.errors import (
    StorageCorruptedError,
    PersistenceError,
)


# Resolve the database directory relative to the project root.
DB_DIR = Path(__file__).resolve().parent.parent / "db"
FILE_PATH = DB_DIR / "data.json"


def initialize() -> None:
    """Create the database directory if it does not exist."""

    DB_DIR.mkdir(parents=True, exist_ok=True)


def save_app_data(tracker_data: WalletEngineData) -> None:
    """Serialize and atomically persist the application state."""

    serialized_data: JSONData = {
        "accounts": {},
        "transactions": [],
    }

    try:
        # Delegate entity serialization to the models.
        for acc_id, account in tracker_data["accounts"].items():
            serialized_data["accounts"][acc_id] = account.to_dict()

        for transaction in tracker_data["transactions"]:
            serialized_data["transactions"].append(
                transaction.to_dict()
            )

        initialize()

        temp_file_path = FILE_PATH.with_suffix(".json.tmp")

        try:
            with open(temp_file_path, "w", encoding="utf-8") as file:
                json.dump(
                    serialized_data,
                    file,
                    indent=4,
                    ensure_ascii=False,
                )
                file.flush()
                os.fsync(file.fileno())

            # Replace the previous file only after writing succeeds.
            os.replace(temp_file_path, FILE_PATH)

        finally:
            # Remove an incomplete temporary file if one remains.
            if temp_file_path.exists():
                temp_file_path.unlink()

    except Exception as err:
        raise PersistenceError(
            "Unable to save application data."
        ) from err


def load_app_data() -> WalletEngineData:
    """Load application data and reconstruct domain entities."""

    empty_data: WalletEngineData = {
        "accounts": {},
        "transactions": [],
    }

    try:
        with open(FILE_PATH, "r", encoding="utf-8") as file:
            raw_data: JSONData = json.load(file)

    except FileNotFoundError:
        # A missing file represents a new application installation.
        try:
            initialize()
        except OSError as err:
            raise PersistenceError(
                "Unable to initialize the database directory."
            ) from err

        return empty_data

    except json.JSONDecodeError as err:
        raise StorageCorruptedError(
            "The application data file contains invalid JSON."
        ) from err

    except (OSError, UnicodeDecodeError) as err:
        raise PersistenceError(
            "Unable to read application data."
        ) from err

    try:
        if not isinstance(raw_data, dict): # type: ignore
            raise ValueError("The root JSON value must be an object.")

        raw_accounts = raw_data.get("accounts")
        raw_transactions = raw_data.get("transactions")

        if not isinstance(raw_accounts, dict): # type: ignore
            raise ValueError("'accounts' must be a JSON object.")

        if not isinstance(raw_transactions, list): # type: ignore
            raise ValueError("'transactions' must be a JSON array.")

        loaded_data: WalletEngineData = {
            "accounts": {},
            "transactions": [],
        }

        # Delegate account reconstruction to Account.from_dict().
        for acc_id, account_data in raw_accounts.items():
            if not isinstance(account_data, dict): # type: ignore
                raise ValueError(
                    f"Account '{acc_id}' must be a JSON object."
                )

            account = Account.from_dict(account_data)

            if account.id != acc_id:
                raise ValueError(
                    f"Account ID mismatch for '{acc_id}'."
                )

            loaded_data["accounts"][acc_id] = account

        # Delegate transaction reconstruction to Transaction.from_dict().
        for transaction_data in raw_transactions:
            if not isinstance(transaction_data, dict): # type: ignore
                raise ValueError(
                    "Each transaction must be a JSON object."
                )

            transaction = Transaction.from_dict(transaction_data)
            loaded_data["transactions"].append(transaction)

        return loaded_data

    except Exception as err:
        raise StorageCorruptedError(
            "The application data file contains invalid or "
            "inconsistent entity records."
        ) from err