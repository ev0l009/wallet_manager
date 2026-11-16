"""Transaction domain model for the Finance Tracker application.

Defines immutable financial transaction records and validates
their individual structural and domain invariants.
"""

from dataclasses import dataclass
from datetime import date
from typing import Self

from exceptions.errors import (
    EntityNotFoundError,
    InvalidAmountError,
    SelfTransferError,
    InvalidTransactionTypeError,
    InvalidCategoryError,
    BusinessRuleError,
)

from models.enums import TrxType, ExpCatOpts
from models.types import TrxDict


@dataclass(frozen=True, kw_only=True)
class Transaction:
    """Represents an immutable financial transaction record."""

    id: str
    amount: int
    transaction_date: date
    transaction_type: str
    category: str | None = None
    desc: str | None = None
    source_acc_id: str | None = None
    target_acc_id: str | None = None
    reverses_transaction_id: str | None = None

    def __post_init__(self) -> None:
        # Transaction ID
        if not isinstance(self.id, str) or not self.id.strip(): # type: ignore
            raise EntityNotFoundError(
                "Transaction ID must be a non-empty string."
            )

        # Amount
        if type(self.amount) is not int or self.amount <= 0:
            raise InvalidAmountError(
                "Transaction amount must be a positive whole number."
            )

        # Transaction date
        if not isinstance(self.transaction_date, date): # type: ignore
            raise BusinessRuleError(
                "Transaction date must be a valid date."
            )

        # Transaction type
        allowed_types = {trx_type.value for trx_type in TrxType}

        if not isinstance(self.transaction_type, str) or ( # type: ignore
            self.transaction_type not in allowed_types
        ):
            raise InvalidTransactionTypeError(
                f"Invalid transaction type: {self.transaction_type!r}."
            )

        # Account references
        for account_id in (self.source_acc_id, self.target_acc_id):
            if account_id is not None and (
                not isinstance(account_id, str) or not account_id.strip() # type: ignore
            ):
                raise EntityNotFoundError(
                    "Account IDs must be non-empty strings when provided."
                )

        # Transaction-specific structural validation
        if self.transaction_type == TrxType.TRANSFER.value:
            if self.source_acc_id is None or self.target_acc_id is None:
                raise EntityNotFoundError(
                    "Transfers require source and target account IDs."
                )

            if self.source_acc_id == self.target_acc_id:
                raise SelfTransferError(
                    "Source and target accounts cannot be the same."
                )

            if self.category is not None:
                raise InvalidCategoryError(
                    "Transfers cannot have an expense category."
                )

        elif self.transaction_type == TrxType.WITHDRAW.value:
            if self.source_acc_id is None:
                raise EntityNotFoundError(
                    "Withdrawals require a source account ID."
                )

            allowed_categories = {
                category.value for category in ExpCatOpts
            }

            if self.category not in allowed_categories:
                raise InvalidCategoryError(
                    f"Invalid expense category: {self.category!r}."
                )

        elif self.transaction_type == TrxType.DEPOSIT.value:
            if self.target_acc_id is None:
                raise EntityNotFoundError(
                    "Deposits require a target account ID."
                )

            if self.category is not None:
                raise InvalidCategoryError(
                    "Deposits cannot have an expense category."
                )

        elif self.transaction_type == TrxType.REVERSAL.value:
            if (
                not isinstance(self.reverses_transaction_id, str)
                or not self.reverses_transaction_id.strip()
            ):
                raise BusinessRuleError(
                    "Reversals must reference an original transaction ID."
                )

            if self.source_acc_id is None and self.target_acc_id is None:
                raise BusinessRuleError(
                    "Reversals must reference at least one account."
                )

    @classmethod
    def from_dict(cls, data: TrxDict) -> Self:
        """Reconstructs a Transaction from a dictionary."""

        transaction_date = data["transaction_date"]

        if isinstance(transaction_date, str): # type: ignore
            transaction_date = date.fromisoformat(transaction_date)

        return cls(
            id=data["id"],
            amount=data["amount"],
            transaction_date=transaction_date,
            transaction_type=data["transaction_type"],
            category=data.get("category"),
            desc=data.get("desc"),
            source_acc_id=data.get("source_acc_id"),
            target_acc_id=data.get("target_acc_id"),
            reverses_transaction_id=data.get(
                "reverses_transaction_id"
            ),
        )

    def to_dict(self) -> TrxDict:
        """Serializes the transaction into a dictionary."""

        return {
            "id": self.id,
            "amount": self.amount,
            "transaction_date": self.transaction_date.isoformat(),
            "transaction_type": self.transaction_type,
            "category": self.category,
            "desc": self.desc,
            "source_acc_id": self.source_acc_id,
            "target_acc_id": self.target_acc_id,
            "reverses_transaction_id": self.reverses_transaction_id,
        }
