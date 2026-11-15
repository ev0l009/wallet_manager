"""Core business workflow engine for the Wallet Manager application.

Coordinates account management, financial operations, domain validation,
and application state transitions.

The engine delegates persistence operations to the Data Access Layer
and contains no direct terminal input or output operations.
"""

import secrets
import string

from copy import deepcopy
from typing import Final

from models.account import Account
from models.transaction import Transaction
from models.types import WalletEngineData
from models.enums import (
    TrxType,
    AccStat
)

# from file_manager.storage import Storage

from utils.validators import (
    convert_to_kobo,
    get_valid_date
)

from exceptions.errors import (
    EntityNotFoundError, 
    WalletError,
    InsufficientFundsError,
    InactiveAccountError,
    AccountBalanceNotZeroError,
    InvalidAccountIdError,
    DuplicateAccountNameError

)

class WalletEngine:
    """Coordinates business workflows and manages application state."""
    ACC_ID_PREFIX: Final[str] = "acc"
    TRX_ID_PREFIX: Final[str] = "trx"

    def __init__(
        self, 
        # storage: "Storage"
    ) -> None:
        """Initialize the wallet engine.

        Args:
            storage: Data Access Layer responsible for loading and
                persisting application data.
        """

        # self.storage = storage

        self.data: WalletEngineData = {
            "accounts": {},
            "transactions": []
        }

    # def load(self) -> None:
    #     """Load persisted application data into active memory."""

    #     self.data = self.storage.load()

    # def save(self) -> None:
    #     """Persist the current application state through the storage layer."""

    #     self.storage.save(self.data)

    def generate_id(self, prefix: str) -> str:
        """Generate a unique identifier for an account or transaction."""

        if prefix not in {self.ACC_ID_PREFIX, self.TRX_ID_PREFIX}:
            raise InvalidAccountIdError(f"Unsupported identifier prefix: {prefix}")

        pool = string.ascii_letters + string.digits

        while True:
            suffix = "".join(secrets.choice(pool) for _ in range(5))
            generated_id = f"{prefix}_{suffix}"

            if prefix == self.ACC_ID_PREFIX:
                if generated_id not in self.data["accounts"]:
                    return generated_id

            elif not any(
                trx.id == generated_id
                for trx in self.data["transactions"]
            ):
                return generated_id

    def create_account(self, acc_name: str, acc_type: str) -> Account:
        """Create and register a new account."""

        normalized_name = acc_name.strip().casefold()

        for account in self.data["accounts"].values():
            if account.acc_name.casefold() == normalized_name:
                raise DuplicateAccountNameError(
                    f"An account named '{acc_name}' already exists."
                )

        new_account = Account(
            id=self.generate_id(self.ACC_ID_PREFIX),
            acc_name=acc_name,
            acc_type=acc_type,
        )

        proposed_data = deepcopy(self.data)
        proposed_data["accounts"][new_account.id] = new_account

        # Persistence will happen here before the in-memory commit.
        self.data = proposed_data

        return new_account
    
    def get_account(self, account_id: str) -> Account:
        """Retrieve an account by ID."""

        account = self.data["accounts"].get(account_id)

        if account is None:
            raise EntityNotFoundError(
                f"Account '{account_id}' does not exist."
            )

        return account
    
    def get_active_accounts(self) -> list[Account]:
        """Return all active accounts."""

        return [
            account
            for account in self.data["accounts"].values()
            if account.acc_status == AccStat.ACTIVE.value
        ]
    
    def _get_active_account(self, acc_id: str) -> Account:
        """Retrieve an account and ensure it is active."""

        account = self.get_account(acc_id)

        if account.acc_status != AccStat.ACTIVE.value:
            raise InactiveAccountError(
                f"Account '{acc_id}' is inactive."
            )

        return account

    def get_inactive_accounts(self) -> list[Account]:
        """Return all inactive accounts."""

        return [
            account
            for account in self.data["accounts"].values()
            if account.acc_status == AccStat.INACTIVE.value
        ]

    def get_active_acc_map(self) -> dict[str, str]:
        """Return active account IDs mapped to account names."""

        return {
            account.id: account.acc_name
            for account in self.get_active_accounts()
        }

    def get_inactive_acc_map(self) -> dict[str, str]:
        """Return inactive account IDs mapped to account names."""

        return {
            account.id: account.acc_name
            for account in self.get_inactive_accounts()
        }

    def get_transactions(self) -> list[Transaction]:
        """Return the complete transaction history, including reversals."""
        return self.data["transactions"].copy()


    def get_effective_transactions(self) -> list[Transaction]:
        """Return transactions whose financial effects remain valid."""

        reversed_transaction_ids = {
            trx.reverses_transaction_id
            for trx in self.data["transactions"]
            if (
                trx.transaction_type == TrxType.REVERSAL.value
                and trx.reverses_transaction_id is not None
            )
        }

        return [
            trx
            for trx in self.data["transactions"]
            if (
                trx.transaction_type != TrxType.REVERSAL.value
                and trx.id not in reversed_transaction_ids
            )
        ]


    def get_acc_bal(self, acc_id: str) -> int:
        """Calculate an account's current balance from effective history."""

        self.get_account(acc_id)

        balance = 0

        for trx in self.get_effective_transactions():

            if trx.transaction_type == TrxType.DEPOSIT.value:
                if trx.target_acc_id == acc_id:
                    balance += trx.amount

            elif trx.transaction_type == TrxType.WITHDRAW.value:
                if trx.source_acc_id == acc_id:
                    balance -= trx.amount

            elif trx.transaction_type == TrxType.TRANSFER.value:
                if trx.source_acc_id == acc_id:
                    balance -= trx.amount

                if trx.target_acc_id == acc_id:
                    balance += trx.amount

        return balance
    

    def record_transfer(
        self,
        source_acc_id: str,
        inp_amt: str,
        target_acc_id: str,
        inp_date: str
    ) -> Transaction:
        """Transfer funds between two accounts."""

        self._get_active_account(source_acc_id)
        self._get_active_account(target_acc_id)

        int_amt = convert_to_kobo(inp_amt)
        valid_date = get_valid_date(inp_date)

        trx = Transaction(
            id=self.generate_id(self.TRX_ID_PREFIX),
            amount=int_amt,
            source_acc_id=source_acc_id,
            target_acc_id=target_acc_id,
            transaction_date=valid_date,
            transaction_type=TrxType.TRANSFER.value,
        )

        source_balance = self.get_acc_bal(source_acc_id)

        if int_amt > source_balance:
            raise InsufficientFundsError(
                "Insufficient funds for this transfer."
            )

        proposed_data = deepcopy(self.data)
        proposed_data["transactions"].append(trx)

        # Persist before committing the in-memory state.
        self.data = proposed_data

        return trx

    def record_income(
        self,
        acc_id: str,
        amount: str,
        desc: str,
        inp_date: str
    ) -> Transaction:
        """Record a deposit into an account."""

        self._get_active_account(acc_id)

        int_amt = convert_to_kobo(amount)
        valid_date = get_valid_date(inp_date)

        trx = Transaction(
            id=self.generate_id(self.TRX_ID_PREFIX),
            amount=int_amt,
            target_acc_id=acc_id,
            desc=desc,
            transaction_date=valid_date,
            transaction_type=TrxType.DEPOSIT.value,
        )

        proposed_data = deepcopy(self.data)
        proposed_data["transactions"].append(trx)

        # Persist before committing the in-memory state.
        self.data = proposed_data

        return trx

    def record_expense(
        self,
        acc_id: str,
        amount: str,
        exp_cat: str,
        desc: str,
        inp_date: str
    ) -> Transaction:
        """Record a withdrawal from an account."""

        self._get_active_account(acc_id)

        int_amt = convert_to_kobo(amount)
        valid_date = get_valid_date(inp_date)

        current_balance = self.get_acc_bal(acc_id)

        if int_amt > current_balance:
            raise InsufficientFundsError(
                "Insufficient funds for this withdrawal."
            )

        trx = Transaction(
            id=self.generate_id(self.TRX_ID_PREFIX),
            amount=int_amt,
            category=exp_cat,
            source_acc_id=acc_id,
            desc=desc,
            transaction_date=valid_date,
            transaction_type=TrxType.WITHDRAW.value,
        )

        proposed_data = deepcopy(self.data)
        proposed_data["transactions"].append(trx)

        # Persist before committing the in-memory state.
        self.data = proposed_data

        return trx

    def reactivate_acc(self, acc_id: str) -> Account:
        """Reactivate an inactive account."""

        self.get_account(acc_id)

        proposed_data = deepcopy(self.data)
        account = proposed_data["accounts"][acc_id]

        account.reactivate()

        # Persistence will happen here before the in-memory commit.
        self.data = proposed_data

        return account

    def deactivate_acc(self, acc_id: str) -> Account:
        """Deactivate an account with a zero balance."""

        self.get_account(acc_id)

        acc_bal = self.get_acc_bal(acc_id)

        if acc_bal != 0:
            raise AccountBalanceNotZeroError(
                "An account must have a zero balance before deactivation."
            )

        proposed_data = deepcopy(self.data)
        account = proposed_data["accounts"][acc_id]

        account.deactivate()

        # Persistence will happen here before the in-memory commit.
        self.data = proposed_data

        return account