"""Data persistence layer for the Wallet Manager application.

Handles JSON serialization and deserialization of application data.
Delegates entity reconstruction to the domain models and uses atomic
file replacement when saving application state.
"""

import json
import os
from pathlib import Path
from typing import Any

from exceptions.errors import (
    DataIntegrityError,
    StorageReadError,
    StorageWriteError,
)

from models.account import Account
from models.transaction import Transaction
from models.types import JSONData, WalletEngineData


# Resolve the database directory relative to the project root.
DB_DIR = Path(__file__).resolve().parent.parent / "db"
FILE_PATH = DB_DIR / "data.json"


def initialize() -> None:
    """Create the database directory if it does not exist."""

    try:
        DB_DIR.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        raise StorageWriteError(
            "Unable to initialize the database directory."
        ) from exc


def save_app_data(tracker_data: WalletEngineData) -> None:
    """Serialize and atomically persist the application state."""

    serialized_data: JSONData = {
        "accounts": {},
        "transactions": [],
    }

    temp_file_path = FILE_PATH.with_suffix(".json.tmp")

    try:
        # Delegate entity serialization to the domain models.
        for acc_id, account in tracker_data["accounts"].items():
            serialized_data["accounts"][acc_id] = account.to_dict()

        for transaction in tracker_data["transactions"]:
            serialized_data["transactions"].append(
                transaction.to_dict()
            )

        initialize()

        with temp_file_path.open("w", encoding="utf-8") as file:
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

    except Exception as exc:
        raise StorageWriteError(
            "Unable to save application data."
        ) from exc

    finally:
        # Remove an incomplete temporary file if one remains.
        try:
            if temp_file_path.exists():
                temp_file_path.unlink()
        except OSError:
            pass


def load_app_data() -> WalletEngineData:
    """Load application data and reconstruct domain entities."""

    empty_data: WalletEngineData = {
        "accounts": {},
        "transactions": [],
    }

    try:
        with FILE_PATH.open("r", encoding="utf-8") as file:
            raw_data: Any = json.load(file)

    except FileNotFoundError:
        # A missing file represents a new application installation.
        initialize()
        return empty_data

    except json.JSONDecodeError as exc:
        raise DataIntegrityError(
            "The application data file contains invalid JSON."
        ) from exc

    except (OSError, UnicodeDecodeError) as exc:
        raise StorageReadError(
            "Unable to read application data."
        ) from exc

    try:
        if not isinstance(raw_data, dict):
            raise ValueError(
                "The root JSON value must be an object."
            )

        expected_keys = {"accounts", "transactions"}

        if set(raw_data) != expected_keys:
            raise ValueError(
                "The root JSON object must contain exactly "
                "'accounts' and 'transactions'."
            )

        raw_accounts = raw_data["accounts"]
        raw_transactions = raw_data["transactions"]

        if not isinstance(raw_accounts, dict):
            raise ValueError("'accounts' must be a JSON object.")

        if not isinstance(raw_transactions, list):
            raise ValueError("'transactions' must be a JSON array.")

        loaded_data: WalletEngineData = {
            "accounts": {},
            "transactions": [],
        }

        # Reconstruct accounts through the domain model.
        for acc_id, account_data in raw_accounts.items():
            if not isinstance(account_data, dict):
                raise ValueError(
                    f"Account '{acc_id}' must be a JSON object."
                )

            account = Account.from_dict(account_data)

            if account.id != acc_id:
                raise ValueError(
                    f"Account ID mismatch for '{acc_id}'."
                )

            loaded_data["accounts"][acc_id] = account

        # Reconstruct transactions through the domain model.
        for transaction_data in raw_transactions:
            if not isinstance(transaction_data, dict):
                raise ValueError(
                    "Each transaction must be a JSON object."
                )

            transaction = Transaction.from_dict(transaction_data)
            loaded_data["transactions"].append(transaction)

        return loaded_data

    except DataIntegrityError:
        raise

    except (KeyError, TypeError, ValueError) as exc:
        raise DataIntegrityError(
            "The application data file contains invalid "
            "or inconsistent entity records."
        ) from exc