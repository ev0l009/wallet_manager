"""Account domain model for the Finance Tracker application.

Defines the immutable Account entity, enforcing account-level invariants,
lifecycle transitions, and explicit dictionary serialization.
"""

from dataclasses import dataclass, replace
from datetime import datetime

from exceptions.errors import (
    BusinessRuleError,
    DataIntegrityError,
    InvalidAccountIdError,
    InvalidAccountNameError,
    InvalidAccountTypeError,
)
from models.enums import AccStat, AccType
from models.types import AccDict

from typing import Self


@dataclass(frozen=True, slots=True)
class Account:
    """Represents a financial account and its lifecycle state."""

    id: str
    acc_name: str
    acc_type: AccType
    created_at: datetime
    acc_status: AccStat = AccStat.ACTIVE

    def __post_init__(self) -> None:
        """Validate and normalize account attributes."""

        # Account ID
        if not isinstance(self.id, str) or not self.id.strip():
            raise InvalidAccountIdError(
                "Account ID must be a non-empty string."
            )

        object.__setattr__(self, "id", self.id.strip())

        # Account name
        if not isinstance(self.acc_name, str):
            raise InvalidAccountNameError(
                "Account name must be a string."
            )

        normalized_name = self.acc_name.strip()

        if not 4 <= len(normalized_name) <= 20:
            raise InvalidAccountNameError(
                "Account name must contain between 4 and 20 characters."
            )

        object.__setattr__(self, "acc_name", normalized_name)

        # Account type
        if not isinstance(self.acc_type, AccType):
            raise InvalidAccountTypeError(
                "Account type must be a valid AccType value."
            )

        # Creation timestamp
        if not isinstance(self.created_at, datetime):
            raise TypeError(
                "created_at must be a datetime instance."
            )

        if (
            self.created_at.tzinfo is None
            or self.created_at.utcoffset() is None
        ):
            raise ValueError(
                "created_at must be timezone-aware."
            )

        # Account status
        if not isinstance(self.acc_status, AccStat):
            raise ValueError(
                "Account status must be a valid AccStat value."
            )

    def rename(self, new_name: str) -> Self:
        """Return a replacement account with an updated name."""

        return replace(self, acc_name=new_name)

    def deactivate(self) -> Self:
        """Return an inactive replacement of this account."""

        if self.acc_status == AccStat.INACTIVE:
            raise BusinessRuleError(
                "Account is already inactive."
            )

        return replace(
            self,
            acc_status=AccStat.INACTIVE,
        )

    def reactivate(self) -> Self:
        """Return an active replacement of this account."""

        if self.acc_status == AccStat.ACTIVE:
            raise BusinessRuleError(
                "Account is already active."
            )

        return replace(
            self,
            acc_status=AccStat.ACTIVE,
        )

    @classmethod
    def from_dict(cls, data: AccDict) -> Self:
        """Reconstruct an Account from persisted dictionary data.

        Invalid persisted account data is reported as DataIntegrityError.
        """

        try:
            if not isinstance(data, dict):
                raise TypeError("Account data must be a dictionary.")

            account_id = data["id"]
            account_name = data["acc_name"]
            account_type = AccType(data["acc_type"])
            account_status = AccStat(data["acc_status"])
            created_at = datetime.fromisoformat(data["created_at"])

            return cls(
                id=account_id,
                acc_name=account_name,
                acc_type=account_type,
                created_at=created_at,
                acc_status=account_status,
            )

        except Exception as exc:
            if isinstance(exc, DataIntegrityError):
                raise

            raise DataIntegrityError(
                f"Invalid persisted account data: {exc}"
            ) from exc

    def to_dict(self) -> AccDict:
        """Convert the account into its JSON-compatible dictionary."""

        return {
            "id": self.id,
            "acc_name": self.acc_name,
            "acc_type": self.acc_type.value,
            "acc_status": self.acc_status.value,
            "created_at": self.created_at.isoformat(),
        }
