"""Transaction domain models for the Finance Tracker application.

Defines an immutable data layer structure modeling financial transfers, 
deposits, and withdrawals using Python data classes.
"""

from dataclasses import dataclass, field
from datetime import date

from exceptions.errors import (
    EntityNotFoundError,
    InvalidAmountError,
    SelfTransferError,
    InvalidTransactionTypeError,
    InvalidCategoryError,
)
from models.enums import (
    TrxType,
    ExpCatOpts,
)
from models.types import (
    TrxDict
)

@dataclass(frozen=True, kw_only=True)
class Transaction:
    """Base immutable schema for all financial transaction entities."""

    id: str
    amount: int
    transaction_date: date
    transaction_type: str = field(init=False)

    def __post_init__(self):
        if not self.id.strip():
            raise EntityNotFoundError("Transaction ID cannot be empty.")
        if type(self.amount) is not int:
            raise InvalidAmountError("Amount must be a valid whole number integer.")
        if self.amount < 0:
            raise InvalidAmountError("Amount cannot be a negative value.")

        # Automatically assign transaction_type based on the class name or a class-level mapping
        trx_type = self._resolve_transaction_type()
        object.__setattr__(self, "transaction_type", trx_type)

    @classmethod
    def _resolve_transaction_type(cls) -> str:
        """Maps the concrete subclass to its corresponding TrxType enum value."""
        type_map = {
            "TransferTrx": TrxType.TRANSFER.value,
            "WithdrawalTrx": TrxType.WITHDRAW.value,
            "DepositTrx": TrxType.DEPOSIT.value,
        }
        trx_type = type_map.get(cls.__name__)
        if not trx_type:
            raise InvalidTransactionTypeError(f"Unsupported transaction class: {cls.__name__}")
        return trx_type

    @classmethod
    def parse_json(cls, data: TrxDict) -> TrxDict:
        """Extracts and sanitizes base fields from a raw dictionary payload."""
        return {
            "id": data["id"],
            "amount": data["amount"],
            "transaction_date": data.get("transaction_date"),
        }


@dataclass(frozen=True, kw_only=True)
class TransferTrx(Transaction):
    """Immutable ledger record representing money moved between two internal accounts."""

    source_acc_id: str
    target_acc_id: str

    def __post_init__(self):
        super().__post_init__()
        if not self.source_acc_id.strip() or not self.target_acc_id.strip():
            raise EntityNotFoundError("Account ID cannot be empty.")
        if self.source_acc_id == self.target_acc_id:
            raise SelfTransferError("Source and target accounts cannot be the same.")


@dataclass(frozen=True, kw_only=True)
class WithdrawalTrx(Transaction):
    """Immutable ledger record representing an outgoing expense from an account."""

    account_id: str
    category: str

    def __post_init__(self):
        super().__post_init__()
        if not self.account_id.strip():
            raise EntityNotFoundError("Account ID cannot be empty.")
        if self.category not in {cat.value for cat in ExpCatOpts}:
            raise InvalidCategoryError(f"Invalid expense category: {self.category}")


@dataclass(frozen=True, kw_only=True)
class DepositTrx(Transaction):
    """Immutable ledger record representing incoming funds into an account."""

    account_id: str

    def __post_init__(self):
        super().__post_init__()
        if not self.account_id.strip():
            raise EntityNotFoundError("Account ID cannot be empty.")
