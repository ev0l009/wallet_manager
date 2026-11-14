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

from ui.menu_states import AccDashState

# from file_manager.storage import Storage

from utils.validators import (
    get_valid_acc_name,
    convert_to_kobo,
    get_valid_date
)

from ui.menus import get_acc_type

from exceptions.errors import (
    EntityNotFoundError, 
    WalletError,
    InsufficientFundsError
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
        """Generate a unique identifier for an account or transaction.

        IDs are generated using a cryptographically secure random
        character pool. Existing records are checked to prevent collisions.

        Args:
            prefix: Identifier prefix, such as 'acc' or 'trx'.

        Returns:
            A unique prefixed identifier.
        """
        
        pool = string.ascii_letters + string.digits

        while True:
            suffix = "".join(
                secrets.choice(pool) for _ in range(5)
            )
            gen_id= f"{prefix}_{suffix}"

            if prefix == self.ACC_ID_PREFIX:
                if gen_id not in self.data["accounts"]:
                    return gen_id

            elif prefix == self.TRX_ID_PREFIX:
                if not any(
                    trx.id == gen_id
                    for trx in self.data["transactions"]
                ):
                    return gen_id

            else:
                raise ValueError(
                    f"Unsupported identifier prefix: {prefix}"
                )

    def create_account(self) -> None:
        """Guide account creation and persist the resulting account.

        New accounts always begin with zero Kobo and ACTIVE status.
        Account-name uniqueness is checked against active and inactive
        accounts.

        Returns:
            Account: The newly created account.
            None: If user input validation fails.
        """

        # Collect existing account names for uniqueness validation.
        existing_names = {
            acc.id: acc.acc_name
            for acc in self.data["accounts"].values()
        }

        # Collect and validate account details.
        try:
            valid_name = get_valid_acc_name(existing_names)
            acc_type = get_acc_type()

        except ValueError as err:
            print(f"\n  [!] Validation Error: {err}")
            return None

        # Generate a system-controlled account identifier.
        account_id = self.generate_id("acc")

        # Construct the account with its mandatory initial state.
        new_account = Account(
            id=account_id,
            acc_name=valid_name,
            acc_type=acc_type,
        )

        # Prepare an isolated proposed application state.
        proposed_data = deepcopy(self.data)

        proposed_data["accounts"][account_id] = new_account

        # Persist before committing the new in-memory state.
        # self.storage.save(proposed_data)

        self.data = proposed_data

        print("\n  [✓] Account created successfully.")


    def get_account(self, account_id: str) -> Account:
        """Retrieve an account using its unique identifier.

        Args:
            account_id: System-generated account identifier.

        Returns:
            The requested Account entity.

        Raises:
            EntityNotFoundError: If the account does not exist.
        """

        account = self.data["accounts"].get(account_id)

        if account is None:
            raise EntityNotFoundError(
                f"Account '{account_id}' does not exist."
            )

        return account

    def get_active_accounts(self) -> list[Account]:
        """Return all accounts currently marked as ACTIVE."""

        return [
            account
            for account in self.data["accounts"].values()
            if account.acc_status == AccStat.ACTIVE.value
        ]

    def get_inactive_accounts(self) -> list[Account]:
        """Return all accounts currently marked as INACTIVE."""

        return [
            account
            for account in self.data["accounts"].values()
            if account.acc_status == AccStat.ACTIVE.value
        ]

    def get_active_acc_map(self) -> dict [str, str]:

        return {
            acc.id: acc.acc_name
            for acc in self.data["accounts"].values()
            if acc.acc_status == AccStat.ACTIVE.value
        }

    def get_inactive_acc_map(self) -> dict [str, str]:
    
        return {
            acc.id: acc.acc_name
            for acc in self.data["accounts"].values()
            if acc.acc_status == AccStat.INACTIVE.value
        }
    
    def get_acc_bal(self, acc_id: str) -> int:
        acc_income = sum([
            trx.amount
            for trx in self.data["transactions"]
            if (
                trx.transaction_type == TrxType.DEPOSIT.value and
                trx.target_acc_id == acc_id
            ) 
        ])

        acc_expense = sum([
            trx.amount
            for trx in self.data["transactions"]
            if (
                trx.transaction_type == TrxType.WITHDRAW.value and
                trx.source_acc_id == acc_id
            ) 
        ])

        return acc_income - acc_expense

    def reactivate_acc(self, acc_id: str):
        self.data["accounts"][acc_id].reactivate()

    def get_transactions(self):
        return [
            trx
            for trx in self.data["transactions"]
            if (trx.transaction_type != TrxType.REVERSAL.value)
        ]

    def record_transfer(
        self,
        source_acc_id: str,
        inp_amt: str,
        target_acc_id: str,
        inp_date: str
    ):
        if source_acc_id not in self.data["accounts"]:
            raise EntityNotFoundError()
        source_acc_bal = self.get_acc_bal(source_acc_id)

        int_amt = convert_to_kobo(inp_amt)

        if int_amt > source_acc_bal:
            raise InsufficientFundsError()
        
        if target_acc_id not in self.data["accounts"]:
            raise EntityNotFoundError()
        valid_date = get_valid_date(inp_date)

        try:
            trx = Transaction(
                id=self.generate_id(self.TRX_ID_PREFIX),
                amount=int_amt,
                source_acc_id=source_acc_id,
                target_acc_id=target_acc_id,
                transaction_date=valid_date,
                transaction_type=TrxType.TRANSFER.value
            )
        except WalletError as err:
            raise
        
        # Prepare an isolated proposed application state.
        proposed_data = deepcopy(self.data)

        proposed_data["transactions"].append(trx)
        proposed_data["accounts"][source_acc_id].debit(int_amt)
        proposed_data["accounts"][target_acc_id].credit(int_amt)

        # Persist before committing the new in-memory state.
        # self.storage.save(proposed_data)

        self.data = proposed_data