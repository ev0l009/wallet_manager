"""Transaction domain models for the Finance Tracker application.

Defines an immutable data layer structure modeling financial transfers, 
deposits, and withdrawals using Python data classes.
"""

from dataclasses import dataclass

from exceptions.errors import (
    EntityNotFoundError,
    InvalidAmountError,
    SelfTransferError,
    InvalidTransactionTypeError
)

from models.types import (
    TrxDict,
    TransferTrxDict
)

from models.enums import TrxType

from datetime import date

@dataclass(frozen=True, kw_only=True)
class Transaction:
    """Base immutable schema for all financial transaction entities."""
    id: str
    amount: int
    transaction_date: date

    def __post_init__(self):
        if not self.id.strip():
            raise EntityNotFoundError("Transaction ID cannot be empty")
        if type(self.amount) is not int:
            raise InvalidAmountError("Amount must be a valid whole number integer.")
        if self.amount < 0:
            raise InvalidAmountError("Amount cannot be a negative value.")

    @classmethod
    def parse_json(cls, data: TrxDict) -> TrxDict:
        """Extracts and sanitizes base fields from a raw dictionary payload."""
        return {
            "id": data["id"],
            "amount": data["amount"],
            "transaction_date": data.get("transaction_date")
        }
    

@dataclass(frozen=True, kw_only=True)
class TransferTrx(Transaction):
    """Immutable ledger record representing money moved between two internal accounts."""

    source_acc_id: str
    target_acc_id: str
    transaction_type: str = TrxType.TRANSFER.value

    def __post_init__(self):
        if not self.source_acc_id.strip() or not self.target_acc_id.strip():
            raise EntityNotFoundError("Account ID cannot be empty")
        if self.source_acc_id == self.target_acc_id:
            raise SelfTransferError("Source and target accounts cannot be thesame for a transfer transaction.")
        if self.transaction_type != TrxType.TRANSFER.value:
            raise InvalidTransactionTypeError("Transaction type must be `transfer` for transfer transactions.")

    def to_dict(self) -> TransferTrxDict:
        """Serializes instance fields into a data-transfer structure."""
        return {
            "id": self.id,
            "amount": self.amount,
            "transaction_date": self.transaction_date,
            "source_acc_id": self.source_acc_id,
            "target_acc_id": self.target_acc_id,
            "transaction_type": self.transaction_type,
        }


@dataclass(frozen=True, kw_only=True)
class DepositTrx(Transaction):
    """Immutable ledger record representing balance inflows added to an account."""

    acc_id: str
    transaction_type: str = TrxType.DEPOSIT.value

    def __post_init__(self):
        if not self.acc_id.strip():
            raise EntityNotFoundError("Account ID cannot be empty")
        if self.transaction_type != TrxType.DEPOSIT.value:
            raise InvalidTransactionTypeError("Transaction type must be `deposit` for deposit transactions.")

    def to_dict(self) -> DepositTrxDict:
        """Serializes instance fields into a data-transfer structure."""
        return {
            "id": self.id,
            "amount": self.amount,
            "acc_id": self.acc_id,
            "timestamp": self.timestamp,
            "transaction_type": self.transaction_type,
        }


@dataclass(frozen=True, kw_only=True)
class WithdrawalTrx(Transaction):
    """Immutable ledger record tracking out-of-pocket expenses or out-of-system outflows."""


    category: str
    transaction_type: str = TrxType.WITHDRAW.value
    acc_id: str

    def __post_init__(self):
        
        
        if self.transaction_type != TrxType.WITHDRAW.value:
            raise InvalidTransactionTypeError("Transaction type must be `withdrawal` for withdrawal transactions.")
        if not self.acc_id.strip():
            raise InvalidIDError("Account ID cannot be empty")
        if self.category not in [item.value for item in ExpCatOpts]:
            raise InvalidCategoryError("Invalid category.")

    def to_dict(self) -> WithdrawalTrxDict:
        """Serializes instance fields into a data-transfer structure."""
        return {
            "id": self.id,
            "amount": self.amount,
            "timestamp": self.timestamp,
            "category": self.category,
            "acc_id": self.acc_id,
            "transaction_type": self.transaction_type
        }