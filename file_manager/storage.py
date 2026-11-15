"""Data persistence layer for the Finance Tracker application.

Handles atomic serialization and deserialization of application data to and
from a JSON storage file, converting between live Python objects/datetimes 
and primitive JSON formats.
"""

from datetime import datetime
import json
import os
from pathlib import Path

from models.account import Account
from models.transaction import Transaction
from models.types import (
    JSONData,
    WalletEngineData
)

# Resolution of relative project paths
DB_DIR = Path(__file__).resolve().parent.parent.parent / "db"
FILE_PATH = DB_DIR / "data.json"


def initialize() -> None:
    """Creates the database directory if it does not already exist."""
    DB_DIR.mkdir(exist_ok=True, parents=True)

 
def save_app_data(tracker_data: WalletEngineData) -> None:
    """Serializes in-memory tracker state and saves it atomically to a JSON file.

    Transforms Account objects into dictionaries and datetime objects into 
    ISO 8601 strings. Uses a temporary file staging technique to guarantee 
    file integrity.
    """
    serialized_data: JSONData = {
        "accounts": {},
        "transactions": []
    }

    # Transform live Account objects into plain dictionaries
    for acc_id, acc in tracker_data.get("accounts", {}).items():
        serialized_data["accounts"][acc_id] = acc.to_dict()

    # Normalize transaction timestamps to ISO strings
    for trx in tracker_data.get("transactions", []):
        serialized_data["transactions"].append(trx.to_dict())

    temp_file_path = FILE_PATH.with_suffix(".json.tmp")

    try:
        # Guarantee parent directory exists before attempting write
        initialize()
        
        with open(temp_file_path, "w", encoding="utf-8") as file:
            json.dump(serialized_data, file, indent=4)
            
        # Atomic replacement swaps temporary file to target filename
        os.replace(temp_file_path, FILE_PATH)
        print("\n  [✓] Session saved successfully.\n")

    except Exception as err:
        print(f"\n  [!] Error: Unable to save session. Details: {err}")
        if temp_file_path.exists():
            temp_file_path.unlink()


def load_app_data() -> WalletEngineData:
    """Loads and deserializes structural records from the primary JSON data file.

    Reconstructs Python datetime objects and parses stored dictionaries back 
    into standard Account model instances.

    Returns:
        TrackerData: An in-memory application dictionary populated with records.
    """
    deserialized_data: WalletEngineData = {
        "accounts": {},
        "transactions": []
    }

    try:
        with open(FILE_PATH, "r", encoding="utf-8") as file:
            raw_data = json.load(file)
            
    except FileNotFoundError:
        print("\n  [i] No saved sessions found. Initializing new ledger...")
        initialize()
        return deserialized_data

    except json.JSONDecodeError:
        print("\n  [!] Alert: Data file is corrupted. Initializing a clean session...\n")
        return deserialized_data

    except Exception as err:
        print(f"\n  [!] Unexpected error loading session: {err}")
        return deserialized_data

    # Hydrate raw dictionary records back into native Python types
    for acc_id, acc in raw_data.get("accounts", {}).items():
        acc_copy = acc.copy()
        created_at = acc_copy.get("created_at")

        if isinstance(created_at, str):
            acc_copy["created_at"] = datetime.fromisoformat(created_at)

        deserialized_data["accounts"][acc_id] = Account(
            id=acc_id,
            acc_name=acc_copy["acc_name"],
            acc_type=acc_copy["acc_type"],
            acc_status=acc_copy["acc_status"],
            created_at=acc_copy["created_at"]
        )

    # Rehydrate transaction timestamps back to datetime objects
    for trx in raw_data.get("transactions", []):
        trx_copy = trx.copy()
        timestamp = trx_copy.get("timestamp")
        trx_type = trx_copy.get("transaction_type")

        if isinstance(timestamp, str):
            trx_copy["timestamp"] = datetime.fromisoformat(timestamp)

        trx_obj = Transaction(
            id=trx_copy["id"],
            amount=trx_copy["amount"],
            transaction_date=trx_copy["transaction_date"],
            transaction_type=trx_copy["transaction_type"],
            category=trx_copy["category"],
            desc=trx_copy["desc"],
            source_acc_id=trx_copy["source_acc_id"],
            target_acc_id=trx_copy["target_acc_id"],
            reverses_transaction_id=trx_copy["reverses_transaction_id"]
        )
        deserialized_data["transactions"].append(trx_obj)

    print("\n  [✓] Session data loaded successfully.")
    return deserialized_data