"""Transaction domain model for the Finance Tracker application.

Defines immutable financial transaction records and validates
their individual structural and domain invariants.
"""

from dataclasses import dataclass
from datetime import date, datetime

from exceptions.errors import (
    DataIntegrityError,
    InvalidAccountIdError,
    InvalidAmountError,
    InvalidCategoryError,
    InvalidDateError,
    InvalidTransactionIdError,
    InvalidTransactionTypeError,
    SelfTransferError,
    ValidationError,
    WalletError,
)

from models.enums import ExpCatOpts, TrxType
from models.types import TrxDict


@dataclass(frozen=True, kw_only=True, slots=True)
class Transaction:
    """Represents an immutable financial transaction record."""

    id: str
    amount: int
    transaction_date: date
    transaction_type: TrxType
    category: ExpCatOpts | None = None
    desc: str | None = None
    source_acc_id: str | None = None
    target_acc_id: str | None = None

    def __post_init__(self) -> None:
        """Validate transaction attributes and structural invariants."""

        # Transaction ID
        if not isinstance(self.id, str) or not self.id.strip():
            raise InvalidTransactionIdError(
                "Transaction ID must be a non-empty string."
            )

        object.__setattr__(self, "id", self.id.strip())

        # Amount: positive integer Kobo
        if type(self.amount) is not int or self.amount <= 0:
            raise InvalidAmountError(
                "Transaction amount must be a positive integer Kobo value."
            )

        # Transaction date
        if (
            not isinstance(self.transaction_date, date)
            or isinstance(self.transaction_date, datetime)
        ):
            raise InvalidDateError(
                "Transaction date must be a date instance, not a datetime."
            )

        # Transaction type
        if not isinstance(self.transaction_type, TrxType):
            raise InvalidTransactionTypeError(
                "Transaction type must be a valid TrxType value."
            )

        # Description
        if self.desc is not None and not isinstance(self.desc, str):
            raise ValidationError(
                "Transaction description must be a string or None."
            )

        # Account references
        for field_name, account_id in (
            ("source", self.source_acc_id),
            ("target", self.target_acc_id),
        ):
            if account_id is not None:
                if not isinstance(account_id, str) or not account_id.strip():
                    raise InvalidAccountIdError(
                        f"{field_name.capitalize()} account ID "
                        "must be a non-empty string when provided."
                    )

        if self.source_acc_id is not None:
            object.__setattr__(
                self, "source_acc_id", self.source_acc_id.strip()
            )

        if self.target_acc_id is not None:
            object.__setattr__(
                self, "target_acc_id", self.target_acc_id.strip()
            )

        # Category type
        if (
            self.category is not None
            and not isinstance(self.category, ExpCatOpts)
        ):
            raise InvalidCategoryError(
                "Category must be a valid expense category or None."
            )

        # Transaction-specific structural validation
        if self.transaction_type == TrxType.INCOME:
            if self.target_acc_id is None:
                raise InvalidAccountIdError(
                    "Income transactions require a target account ID."
                )

            if self.source_acc_id is not None:
                raise ValidationError(
                    "Income transactions cannot have a source account."
                )

            if self.category is not None:
                raise InvalidCategoryError(
                    "Income transactions cannot have an expense category."
                )

        elif self.transaction_type == TrxType.EXPENSE:
            if self.source_acc_id is None:
                raise InvalidAccountIdError(
                    "Expense transactions require a source account ID."
                )

            if self.target_acc_id is not None:
                raise ValidationError(
                    "Expense transactions cannot have a target account."
                )

            if self.category is None:
                raise InvalidCategoryError(
                    "Expense transactions require an expense category."
                )

        elif self.transaction_type == TrxType.TRANSFER:
            if (
                self.source_acc_id is None
                or self.target_acc_id is None
            ):
                raise InvalidAccountIdError(
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

    @classmethod
    def from_dict(cls, data: TrxDict) -> "Transaction":
        """Reconstruct a Transaction from persisted dictionary data.

        Invalid persisted transaction records raise DataIntegrityError.
        """

        try:
            if not isinstance(data, dict):
                raise TypeError(
                    "Transaction data must be a dictionary."
                )

            # Reject fields outside the defined persistence schema.
            allowed_keys = {
                "id",
                "amount",
                "transaction_date",
                "transaction_type",
                "category",
                "desc",
                "source_acc_id",
                "target_acc_id",
            }

            unexpected_keys = [
                key for key in data if key not in allowed_keys
            ]

            if unexpected_keys:
                raise ValueError(
                    f"Unexpected transaction fields: {unexpected_keys}."
                )

            # Date must use the exact YYYY-MM-DD representation.
            date_value = data["transaction_date"]

            if not isinstance(date_value, str):
                raise TypeError(
                    "Persisted transaction date must be a string."
                )

            transaction_date = date.fromisoformat(date_value)

            if transaction_date.isoformat() != date_value:
                raise ValueError(
                    "Transaction date must use YYYY-MM-DD format."
                )

            # Transaction type must be stored as a string.
            transaction_type_value = data["transaction_type"]

            if not isinstance(transaction_type_value, str):
                raise TypeError(
                    "Persisted transaction type must be a string."
                )

            # Category must be a string or None.
            category_value = data.get("category")

            if (
                category_value is not None
                and not isinstance(category_value, str)
            ):
                raise TypeError(
                    "Persisted transaction category must be a string or None."
                )

            category = (
                ExpCatOpts(category_value)
                if category_value is not None
                else None
            )

            return cls(
                id=data["id"],
                amount=data["amount"],
                transaction_date=transaction_date,
                transaction_type=TrxType(transaction_type_value),
                category=category,
                desc=data.get("desc"),
                source_acc_id=data.get("source_acc_id"),
                target_acc_id=data.get("target_acc_id"),
            )

        except (KeyError, TypeError, ValueError, WalletError) as exc:
            raise DataIntegrityError(
                f"Invalid persisted transaction data: {exc}"
            ) from exc

    def to_dict(self) -> TrxDict:
        """Convert the transaction into a JSON-compatible dictionary."""

        return {
            "id": self.id,
            "amount": self.amount,
            "transaction_date": self.transaction_date.isoformat(),
            "transaction_type": self.transaction_type.value,
            "category": (
                self.category.value
                if self.category is not None
                else None
            ),
            "desc": self.desc,
            "source_acc_id": self.source_acc_id,
            "target_acc_id": self.target_acc_id,
        }