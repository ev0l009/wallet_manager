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

from file_manager.storage import (
    save_app_data,
    load_app_data
)
 
from utils.validators import (
    convert_to_kobo,
    get_valid_date
)

from exceptions.errors import (
    EntityNotFoundError, 
    InsufficientFundsError,
    InactiveAccountError,
    AccountBalanceNotZeroError,
    InvalidAccountIdError,
    DuplicateAccountNameError,
    InvalidReversalError,
    TransactionAlreadyReversedError,
    StorageCorruptedError
)

class WalletEngine:
    """Coordinates business workflows and manages application state."""
    ACC_ID_PREFIX: Final[str] = "acc"
    TRX_ID_PREFIX: Final[str] = "trx"

    def __init__(
        self, 
    ) -> None:
        """Initialize the wallet engine.

        Args:
            storage: Data Access Layer responsible for loading and
                persisting application data.
        """

        self.data: WalletEngineData = {
            "accounts": {},
            "transactions": []
        }

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

        self._commit(proposed_data)

        return deepcopy(new_account)
    
    def get_account(self, account_id: str) -> Account:
        """Retrieve a detached copy of an account by ID."""

        account = self.data["accounts"].get(account_id)

        if account is None:
            raise EntityNotFoundError(
                f"Account '{account_id}' does not exist."
            )

        return deepcopy(account)
    
    def get_active_accounts(self) -> list[Account]:
        """Return detached copies of all active accounts."""

        return [
            deepcopy(account)
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
        """Return detached copies of all inactive accounts."""

        return [
            deepcopy(account)
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
        """Return detached copies of the complete transaction history."""

        return deepcopy(self.data["transactions"])


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

        proposed_transactions = (
            self.data["transactions"] + [trx]
        )

        self._validate_chronological_balances(
            proposed_transactions
        )

        proposed_data = deepcopy(self.data)
        proposed_data["transactions"].append(trx)

        self._commit(proposed_data)

        return deepcopy(trx)

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

        proposed_transactions = (
            self.data["transactions"] + [trx]
        )

        self._validate_chronological_balances(
            proposed_transactions
        )

        proposed_data = deepcopy(self.data)
        proposed_data["transactions"].append(trx)

        self._commit(proposed_data)

        return deepcopy(trx)

    def record_expense(
        self,
        acc_id: str,
        amount: str,
        exp_cat: str,
        desc: str,
        inp_date: str
    ) -> Transaction:

        self._get_active_account(acc_id)

        int_amt = convert_to_kobo(amount)
        valid_date = get_valid_date(inp_date)

        trx = Transaction(
            id=self.generate_id(self.TRX_ID_PREFIX),
            amount=int_amt,
            category=exp_cat,
            source_acc_id=acc_id,
            desc=desc,
            transaction_date=valid_date,
            transaction_type=TrxType.WITHDRAW.value,
        )

        proposed_transactions = (
            self.data["transactions"] + [trx]
        )

        self._validate_chronological_balances(
            proposed_transactions
        )

        proposed_data = deepcopy(self.data)
        proposed_data["transactions"].append(trx)

        self._commit(proposed_data)

        return deepcopy(trx)
    
    def get_transaction(self, trx_id: str) -> Transaction:
        """Retrieve a detached copy of a transaction by ID."""

        for trx in self.data["transactions"]:
            if trx.id == trx_id:
                return deepcopy(trx)

        raise EntityNotFoundError(
            f"Transaction '{trx_id}' does not exist."
        )
    
    def record_reversal(
        self,
        original_trx_id: str,
        inp_date: str
    ) -> Transaction:
        """Reverse an existing transaction."""

        original = self.get_transaction(original_trx_id)

        if original.transaction_type == TrxType.REVERSAL.value:
            raise InvalidReversalError(
                "A reversal transaction cannot itself be reversed."
            )

        already_reversed = any(
            trx.transaction_type == TrxType.REVERSAL.value
            and trx.reverses_transaction_id == original.id
            for trx in self.data["transactions"]
        )

        if already_reversed:
            raise TransactionAlreadyReversedError(
                "This transaction has already been reversed."
            )

        valid_date = get_valid_date(inp_date)

        affected_account_ids = {
            original.source_acc_id,
            original.target_acc_id,
        } - {None}

        for account_id in affected_account_ids:
            account = self.get_account(account_id) # type: ignore

            if account.acc_status != AccStat.ACTIVE.value:
                raise InactiveAccountError(
                    f"Cannot reverse transaction: account "
                    f"'{account.acc_name}' is inactive."
                )

        reversal = Transaction(
            id=self.generate_id(self.TRX_ID_PREFIX),
            amount=original.amount,
            source_acc_id=original.source_acc_id,
            target_acc_id=original.target_acc_id,
            transaction_date=valid_date,
            transaction_type=TrxType.REVERSAL.value,
            reverses_transaction_id=original.id,
        )

        proposed_transactions = (
            self.data["transactions"] + [reversal]
        )

        self._validate_chronological_balances(
            proposed_transactions
        )

        proposed_data = deepcopy(self.data)
        proposed_data["transactions"].append(reversal)

        self._commit(proposed_data)

        return deepcopy(reversal)

    
    def reactivate_acc(self, acc_id: str) -> Account:
        """Reactivate an inactive account."""

        self.get_account(acc_id)

        proposed_data = deepcopy(self.data)
        account = proposed_data["accounts"][acc_id]

        account.reactivate()

        self._commit(proposed_data)

        return deepcopy(account)


    
    def deactivate_acc(self, acc_id: str) -> Account:
        """Deactivate an active account with a zero balance."""

        self._get_active_account(acc_id)

        acc_bal = self.get_acc_bal(acc_id)

        if acc_bal != 0:
            raise AccountBalanceNotZeroError(
                "An account must have a zero balance before deactivation."
            )

        proposed_data = deepcopy(self.data)
        account = proposed_data["accounts"][acc_id]

        account.deactivate()

        self._commit(proposed_data)

        return deepcopy(account)

    def _commit(self, proposed_data: WalletEngineData) -> None:
        """Persist proposed state before committing it in memory."""

        save_app_data(proposed_data)
        self.data = proposed_data

    @staticmethod
    def _build_effective_transactions(
        transactions: list[Transaction]
    ) -> list[Transaction]:
        """Build effective history from a supplied transaction collection."""

        reversed_ids = {
            trx.reverses_transaction_id
            for trx in transactions
            if (
                trx.transaction_type == TrxType.REVERSAL.value
                and trx.reverses_transaction_id is not None
            )
        }

        return [
            trx
            for trx in transactions
            if (
                trx.transaction_type != TrxType.REVERSAL.value
                and trx.id not in reversed_ids
            )
        ]


    def get_effective_transactions(self) -> list[Transaction]:
        """Return detached copies of transactions with valid financial effects."""

        return deepcopy(
            self._build_effective_transactions(
                self.data["transactions"]
            )
        )

    def get_reports(self) -> tuple[ int, int, int, dict[str, int] ]:
        effective_transactions = self.get_effective_transactions()
        total_income = sum([
            trx.amount for trx in effective_transactions
            if trx.transaction_type == TrxType.DEPOSIT.value
        ])

        total_expense = sum([
            trx.amount for trx in effective_transactions
            if trx.transaction_type == TrxType.WITHDRAW.value
        ])

        net_delta = total_income - total_expense

        expenses_by_category = {}

        for trx in effective_transactions:
            if trx.transaction_type == TrxType.WITHDRAW.value:
                if trx.category not  in expenses_by_category:
                    expenses_by_category[trx.category] = trx.amount
                expenses_by_category[trx.category] += trx.amount

        return total_income, total_expense, net_delta, expenses_by_category


    def _validate_chronological_balances(
        self,
        transactions: list[Transaction],
        accounts: dict[str, Account] | None = None,
    ) -> None:
        """Ensure no account has a negative balance at any point in history."""

        if accounts is None:
            accounts = self.data["accounts"]

        effective_transactions = self._build_effective_transactions(
            transactions
        )

        # Stable sorting preserves insertion order for transactions
        # sharing the same transaction date.
        ordered_transactions = sorted(
            effective_transactions,
            key=lambda trx: trx.transaction_date,
        )

        balances = {
            acc_id: 0
            for acc_id in accounts
        }

        for trx in ordered_transactions:

            if trx.transaction_type == TrxType.DEPOSIT.value:
                target_id = trx.target_acc_id

                if target_id not in balances:
                    raise EntityNotFoundError(
                        f"Transaction '{trx.id}' references an "
                        f"unknown target account."
                    )

                balances[target_id] += trx.amount

            elif trx.transaction_type == TrxType.WITHDRAW.value:
                source_id = trx.source_acc_id

                if source_id not in balances:
                    raise EntityNotFoundError(
                        f"Transaction '{trx.id}' references an "
                        f"unknown source account."
                    )

                balances[source_id] -= trx.amount

                if balances[source_id] < 0:
                    raise InsufficientFundsError(
                        f"Transaction '{trx.id}' creates a negative "
                        f"historical balance for account '{source_id}'."
                    )

            elif trx.transaction_type == TrxType.TRANSFER.value:
                source_id = trx.source_acc_id
                target_id = trx.target_acc_id

                if source_id not in balances or target_id not in balances:
                    raise EntityNotFoundError(
                        f"Transfer '{trx.id}' references an "
                        f"unknown account."
                    )

                balances[source_id] -= trx.amount

                if balances[source_id] < 0:
                    raise InsufficientFundsError(
                        f"Transfer '{trx.id}' creates a negative "
                        f"historical balance for account '{source_id}'."
                    )

                balances[target_id] += trx.amount

    def _validate_loaded_data(self, loaded_data: WalletEngineData) -> None:
        """Validate cross-entity references and financial consistency."""

        accounts = loaded_data["accounts"]
        transactions = loaded_data["transactions"]

        transaction_map: dict[str, Transaction] = {}

        # Transaction IDs must be unique.
        for trx in transactions:
            if trx.id in transaction_map:
                raise ValueError(
                    f"Duplicate transaction ID: '{trx.id}'."
                )

            transaction_map[trx.id] = trx

        # Validate reversal relationships.
        reversed_ids: set[str] = set()

        for trx in transactions:
            if trx.transaction_type != TrxType.REVERSAL.value:
                continue

            original_id = trx.reverses_transaction_id

            if original_id is None or original_id not in transaction_map:
                raise ValueError(
                    f"Reversal '{trx.id}' references a missing transaction."
                )

            original = transaction_map[original_id]

            if original.transaction_type == TrxType.REVERSAL.value:
                raise ValueError(
                    f"Reversal '{trx.id}' attempts to reverse another reversal."
                )

            if original_id in reversed_ids:
                raise ValueError(
                    f"Transaction '{original_id}' has multiple reversals."
                )

            if (
                trx.amount != original.amount
                or trx.source_acc_id != original.source_acc_id
                or trx.target_acc_id != original.target_acc_id
            ):
                raise ValueError(
                    f"Reversal '{trx.id}' does not match its original transaction."
                )

            reversed_ids.add(original_id)

        # Validate account references and chronological financial consistency.
        self._validate_chronological_balances(
            transactions,
            accounts,
        )

    def load(self) -> None:
        """Load and validate persisted application data."""

        loaded_data = load_app_data()

        try:
            self._validate_loaded_data(loaded_data)

        except Exception as err:
            raise StorageCorruptedError(
                "Persisted application data failed business validation."
            ) from err

        self.data = loaded_data