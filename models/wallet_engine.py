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
from models.types import WalletEngineData
from models.enums import (
    TrxType
)

from ui.menus import get_acc_dash_state

# from file_manager.storage import Storage

from utils.validators import get_valid_acc_name

from ui.menus import get_acc_type

from exceptions.errors import (
    EntityNotFoundError
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
            if account.acc_status == "ACTIVE"
        ]

    def get_inactive_accounts(self) -> list[Account]:
        """Return all accounts currently marked as INACTIVE."""

        return [
            account
            for account in self.data["accounts"].values()
            if account.acc_status == "INACTIVE"
        ]

    def get_acc_map(self) -> dict [str, str]:

        return {
            acc.id: acc.acc_name
            for acc in self.data["accounts"].values()
        }
    
    def get_acc_bal(self, acc_id: str) -> int:
        acc_income = sum([
            trx.amount
            for trx in self.data["transactions"]
            if trx.transaction_type == TrxType.DEPOSIT.value
        ])

        acc_expense = sum([
            trx.amount
            for trx in self.data["transactions"]
            if trx.transaction_type == TrxType.WITHDRAW.value
        ])

        return acc_income - acc_expense