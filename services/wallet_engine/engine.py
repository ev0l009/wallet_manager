"""Core business workflow engine for the Wallet Manager application.

Owns application state and coordinates persistence and business operations.
Specific workflows are delegated to dedicated wallet_engine modules.
"""

from typing import Final

from models.account import Account
from models.transaction import Transaction
from models.types import WalletEngineData

from file_manager.storage import (
    save_app_data,
    load_app_data,
)

from services.wallet_engine import accounts
from services.wallet_engine import transactions
from services.wallet_engine import ledger
from services.wallet_engine import reports

from services.wallet_engine.identifiers import (
    generate_id,
    ACC_ID_PREFIX,
    TRX_ID_PREFIX,
)

from services.wallet_engine.validation import validate_loaded_data


class WalletEngine:
    """Coordinates business workflows and manages application state."""

    ACC_ID_PREFIX: Final[str] = ACC_ID_PREFIX
    TRX_ID_PREFIX: Final[str] = TRX_ID_PREFIX

    def __init__(self) -> None:
        """Initialize the wallet engine with an empty application state."""

        self.data: WalletEngineData = {
            "accounts": {},
            "transactions": [],
        }

    # ---------------------------------------------------------
    # Persistence and state management
    # ---------------------------------------------------------

    def load(self) -> None:
        """Load and validate persisted application data."""

        loaded_data = load_app_data()

        validate_loaded_data(loaded_data)

        # Replace active state only after successful loading and validation.
        self.data = loaded_data

    def _commit(self, proposed_data: WalletEngineData) -> None:
        """Persist proposed state before committing it in memory."""

        validate_loaded_data(proposed_data)

        save_app_data(proposed_data)

        # In-memory state changes only after persistence succeeds.
        self.data = proposed_data

    @staticmethod
    def _validate_loaded_data(
        loaded_data: WalletEngineData,
    ) -> None:
        """Validate application data and its financial integrity."""

        validate_loaded_data(loaded_data)

    # ---------------------------------------------------------
    # Identifier generation
    # ---------------------------------------------------------

    def generate_id(self, prefix: str) -> str:
        """Generate a unique account or transaction identifier."""

        return generate_id(prefix, self.data)

    # ---------------------------------------------------------
    # Account management
    # ---------------------------------------------------------

    def create_account(
        self,
        acc_name: str,
        acc_type: str,
    ) -> Account:
        """Create and register a new account."""

        proposed_data, account = accounts.create_account(
            self.data,
            acc_name,
            acc_type,
        )

        self._commit(proposed_data)

        return account

    def update_account_name(
        self,
        acc_id: str,
        acc_name: str,
    ) -> Account:
        """Update an account's name."""

        proposed_data, account = accounts.rename_account(
            self.data,
            acc_id,
            acc_name,
        )

        self._commit(proposed_data)

        return account

    def get_account(self, account_id: str) -> Account:
        """Retrieve an account by ID."""

        return accounts.get_account(self.data, account_id)

    def get_active_accounts(self) -> list[Account]:
        """Return all active accounts."""

        return accounts.get_active_accounts(self.data)

    def _get_active_account(self, acc_id: str) -> Account:
        """Retrieve an account and ensure it is active."""

        return accounts.get_active_account(self.data, acc_id)

    def get_inactive_accounts(self) -> list[Account]:
        """Return all inactive accounts."""

        return accounts.get_inactive_accounts(self.data)

    def get_all_accounts(self) -> list[Account]:
        """Return all accounts."""

        return accounts.get_all_accounts(self.data)

    def get_all_acc_map(self) -> dict[str, str]:
        """Return all account IDs mapped to account names."""

        return accounts.get_all_account_map(self.data)

    def get_active_acc_map(self) -> dict[str, str]:
        """Return active account IDs mapped to account names."""

        return accounts.get_active_account_map(self.data)

    def get_inactive_acc_map(self) -> dict[str, str]:
        """Return inactive account IDs mapped to account names."""

        return accounts.get_inactive_account_map(self.data)

    def reactivate_acc(self, acc_id: str) -> Account:
        """Reactivate an inactive account."""

        proposed_data, account = accounts.reactivate_account(
            self.data,
            acc_id,
        )

        self._commit(proposed_data)

        return account

    def deactivate_acc(self, acc_id: str) -> Account:
        """Deactivate an active account with a zero balance."""

        balance = self.get_acc_bal(acc_id)

        proposed_data, account = accounts.deactivate_account(
            self.data,
            acc_id,
            balance,
        )

        self._commit(proposed_data)

        return account

    # ---------------------------------------------------------
    # Transaction management
    # ---------------------------------------------------------

    def get_transactions(self) -> list[Transaction]:
        """Return the complete transaction history."""

        return transactions.get_transactions(self.data)

    def get_transaction(self, trx_id: str) -> Transaction:
        """Retrieve a transaction by ID."""

        return transactions.get_transaction(self.data, trx_id)

    def record_income(
        self,
        acc_id: str,
        amount: str,
        desc: str,
        inp_date: str,
    ) -> Transaction:
        """Record income into an account."""

        proposed_data, transaction = transactions.record_income(
            self.data,
            acc_id,
            amount,
            desc,
            inp_date,
        )

        self._commit(proposed_data)

        return transaction

    def record_expense(
        self,
        acc_id: str,
        amount: str,
        exp_cat: str,
        desc: str,
        inp_date: str,
    ) -> Transaction:
        """Record an expense from an account."""

        proposed_data, transaction = transactions.record_expense(
            self.data,
            acc_id,
            amount,
            exp_cat,
            desc,
            inp_date,
        )

        self._commit(proposed_data)

        return transaction

    def record_transfer(
        self,
        source_acc_id: str,
        inp_amt: str,
        target_acc_id: str,
        inp_date: str,
    ) -> Transaction:
        """Transfer funds between two accounts."""

        proposed_data, transaction = transactions.record_transfer(
            self.data,
            source_acc_id,
            inp_amt,
            target_acc_id,
            inp_date,
        )

        self._commit(proposed_data)

        return transaction

    # ---------------------------------------------------------
    # Ledger operations
    # ---------------------------------------------------------

    def get_acc_bal(self, acc_id: str) -> int:
        """Calculate an account's current balance from its history."""

        self.get_account(acc_id)

        return ledger.calculate_account_balance(
            self.data["transactions"],
            acc_id,
        )

    def get_effective_transactions(self) -> list[Transaction]:
        """Return the complete transaction history.

        Retained as a compatibility method. Transactions are no longer
        filtered because the application does not use reversal records.
        """

        return self.get_transactions()

    def get_acc_transactions(
        self,
        acc_id: str,
    ) -> list[Transaction]:
        """Return transactions involving the specified account."""

        self.get_account(acc_id)

        return ledger.get_account_transactions(
            self.data["transactions"],
            acc_id,
        )

    # ---------------------------------------------------------
    # Financial reports
    # ---------------------------------------------------------

    def get_reports(
        self,
    ) -> tuple[int, int, int, dict[str, int]]:
        """Generate an overall financial summary."""

        return reports.get_reports(self.data)

    def get_account_reports(
        self,
        acc_id: str,
    ) -> tuple[int, int, int, dict[str, int]]:
        """Generate a financial summary for one account."""

        return reports.get_account_reports(self.data, acc_id)