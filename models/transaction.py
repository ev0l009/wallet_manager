"""Transaction domain models for the Finance Tracker application.

Defines an immutable data layer structure modeling financial transfers, 
deposits, and withdrawals using Python data classes.
"""

from dataclasses import dataclass
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
    transaction_type: str
    category: str | None = None
    desc: str | None = None
    source_acc_id: str
    target_acc_id: str
    transaction_date: date
    reverses_transaction_id: str | None = None

    def __post_init__(self):
        if not self.id.strip():
            raise EntityNotFoundError("Transaction ID cannot be empty.")
        
        if type(self.amount) is not int:
            raise InvalidAmountError("Amount must be a valid whole number integer.")
        if self.amount < 0:
            raise InvalidAmountError("Amount cannot be a negative value.")
        
        if self.transaction_type == TrxType.TRANSFER.value:
            if not self.source_acc_id.strip() or not self.target_acc_id.strip():
                raise EntityNotFoundError("Account ID cannot be empty.")
            if self.source_acc_id == self.target_acc_id:
                raise SelfTransferError("Source and target accounts cannot be the same.")

        elif self.transaction_type == TrxType.WITHDRAW.value:
            if not self.source_acc_id.strip():
                raise EntityNotFoundError("Account ID cannot be empty.")
            if self.category not in {cat.value for cat in ExpCatOpts}:
                raise InvalidCategoryError(f"Invalid expense category: {self.category}")

        elif self.transaction_type == TrxType.DEPOSIT.value:
            if not self.target_acc_id.strip():
                raise EntityNotFoundError("Account ID cannot be empty.")

        else:
            raise InvalidTransactionTypeError("Inavalid transaction type")

    @classmethod
    def parse_json(cls, data: TrxDict) -> TrxDict:
        """Extracts and sanitizes base fields from a raw dictionary payload."""
        return {
            "id": data["id"],
            "amount": data["amount"],
            "transaction_date": data.get("transaction_date"),
            "transaction_type": data["transaction_type"],
            "category": data["category"],
            "desc": data["desc"],
            "source_acc_id": data["source_acc_id"],
            "target_acc_id": data["source_acc_id"],
            "reverses_transaction_id": data["reverses_transaction_id"]
        }