"""Core business workflow engine for the Wallet Manager application.

Owns application state and coordinates persistence and business operations.
Specific workflows are delegated to dedicated wallet_engine modules.
"""

from models.account import Account
from models.transaction import Transaction
from models.enums import TrxType
from models.types import WalletEngineData

from file_manager.storage import save_app_data, load_app_data

from exceptions.errors import (
    DataIntegrityError,
    NegativeBalanceError,
)


class WalletEngine:
    """Coordinates business workflows and manages application state."""

    def __init__(self) -> None:
        """Initialize the wallet engine with an empty application state."""

        self.data: WalletEngineData = {
            "accounts": {},
            "transactions": [],
        }

    def load(self) -> None:
        """Load and validate persisted application data."""

        loaded_data = load_app_data()

        self._validate_loaded_data(loaded_data)

        # Replace active state only after successful loading and validation.
        self.data = loaded_data

    def _commit(self, proposed_data: WalletEngineData) -> None:
        """Persist proposed state before committing it in memory."""

        self._validate_loaded_data(proposed_data)

        save_app_data(proposed_data)

        # In-memory state changes only after persistence succeeds.
        self.data = proposed_data

    @staticmethod
    def _validate_loaded_data(
        loaded_data: WalletEngineData,
    ) -> None:
        """Validate entity relationships and historical ledger integrity."""

        accounts = loaded_data["accounts"]
        transactions = loaded_data["transactions"]

        # Validate account dictionary keys and account-name uniqueness.
        account_names: set[str] = set()

        for account_id, account in accounts.items():
            if account_id != account.id:
                raise DataIntegrityError(
                    f"Account dictionary key does not match "
                    f"account ID '{account.id}'."
                )

            normalized_name = account.acc_name.casefold()

            if normalized_name in account_names:
                raise DataIntegrityError(
                    f"Duplicate account name: '{account.acc_name}'."
                )

            account_names.add(normalized_name)

        # Transaction IDs must be unique.
        transaction_ids: set[str] = set()

        for transaction in transactions:
            if transaction.id in transaction_ids:
                raise DataIntegrityError(
                    f"Duplicate transaction ID: '{transaction.id}'."
                )

            transaction_ids.add(transaction.id)

            # Validate account references.
            referenced_account_ids = {
                transaction.source_acc_id,
                transaction.target_acc_id,
            } - {None}

            for account_id in referenced_account_ids:
                if account_id not in accounts:
                    raise DataIntegrityError(
                        f"Transaction '{transaction.id}' references "
                        f"unknown account '{account_id}'."
                    )

        # Validate historical balances.
        # Python's sort is stable, preserving insertion order for
        # transactions sharing the same financial date.
        ordered_transactions = sorted(
            transactions,
            key=lambda transaction: transaction.transaction_date,
        )

        balances = {
            account_id: 0
            for account_id in accounts
        }

        for transaction in ordered_transactions:
            if transaction.transaction_type == TrxType.INCOME:
                target_id = transaction.target_acc_id
                balances[target_id] += transaction.amount

            elif transaction.transaction_type == TrxType.EXPENSE:
                source_id = transaction.source_acc_id
                balances[source_id] -= transaction.amount

                if balances[source_id] < 0:
                    raise NegativeBalanceError(
                        f"Transaction '{transaction.id}' creates a "
                        f"negative historical balance for account "
                        f"'{source_id}' on "
                        f"{transaction.transaction_date}: "
                        f"{balances[source_id]} Kobo."
                    )

            elif transaction.transaction_type == TrxType.TRANSFER:
                source_id = transaction.source_acc_id
                target_id = transaction.target_acc_id

                balances[source_id] -= transaction.amount

                if balances[source_id] < 0:
                    raise NegativeBalanceError(
                        f"Transfer '{transaction.id}' creates a "
                        f"negative historical balance for account "
                        f"'{source_id}' on "
                        f"{transaction.transaction_date}: "
                        f"{balances[source_id]} Kobo."
                    )

                balances[target_id] += transaction.amount