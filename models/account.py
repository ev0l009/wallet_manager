
"""Account domain model for the Finance Tracker application.

Defines the Account entity, enforcing account-level invariants,
lifecycle transitions, and explicit dictionary serialization.
"""

from datetime import datetime, timezone
from typing import Self

from exceptions.errors import (
    InvalidAccountNameError,
    InvalidAccountTypeError,
    BusinessRuleError,
    StorageCorruptedError
)

from models.enums import AccType, AccStat
from models.types import AccDict


class Account:
    """Represents a financial account and its lifecycle state."""

    def __init__(
        self,
        id: str,
        acc_name: str,
        acc_type: str,
        created_at: datetime | None = None,
    ) -> None:
        # Account identifier
        if not isinstance(id, str) or not id.strip(): # type: ignore
            raise ValueError("Account ID must be a non-empty string.")

        self._id = id.strip()

        # Account name
        self.acc_name = acc_name

        # Account type
        allowed_types = {account_type.value for account_type in AccType}

        if acc_type not in allowed_types:
            raise InvalidAccountTypeError(
                f"Invalid account type '{acc_type}'. "
                f"Must be one of {allowed_types}."
            )

        self._acc_type = acc_type

        # Creation timestamp
        if created_at is None:
            created_at = datetime.now(timezone.utc).replace(microsecond=0)

        if not isinstance(created_at, datetime): # type: ignore
            raise TypeError("created_at must be a datetime instance.")

        if created_at.tzinfo is None or created_at.utcoffset() is None:
            raise ValueError("created_at must be timezone-aware.")

        self._created_at = created_at

        # Initial lifecycle state
        self._acc_status = AccStat.ACTIVE.value

    # --- READ-ONLY PROPERTIES ---

    @property
    def id(self) -> str:
        """Returns the account's unique identifier."""
        return self._id

    @property
    def acc_type(self) -> str:
        """Returns the account classification."""
        return self._acc_type

    @property
    def created_at(self) -> datetime:
        """Returns the account creation timestamp."""
        return self._created_at

    @property
    def acc_status(self) -> str:
        """Returns the account's current lifecycle state."""
        return self._acc_status

    # --- MUTABLE PROPERTIES ---

    @property
    def acc_name(self) -> str:
        """Returns the account name."""
        return self._acc_name

    @acc_name.setter
    def acc_name(self, value: str) -> None:
        """Validates and updates the account name."""

        if not isinstance(value, str):
            raise InvalidAccountNameError(
                "Account name must be a string."
            )

        value = value.strip()

        if not value:
            raise InvalidAccountNameError(
                "Account name cannot be empty."
            )

        if len(value) < 4:
            raise InvalidAccountNameError(
                "Account name must contain at least four characters."
            )

        self._acc_name = value

    # --- LIFECYCLE METHODS ---

    def deactivate(self) -> None:
        """Transitions an active account to inactive."""

        if self.acc_status == AccStat.INACTIVE.value:
            raise BusinessRuleError(
                "Account is already inactive."
            )

        self._acc_status = AccStat.INACTIVE.value

    def reactivate(self) -> None:
        """Transitions an inactive account to active."""

        if self.acc_status == AccStat.ACTIVE.value:
            raise BusinessRuleError(
                "Account is already active."
            )

        self._acc_status = AccStat.ACTIVE.value

    # --- SERIALIZATION ---

    @classmethod
    def from_dict(cls, data: AccDict) -> Self:
        """Reconstructs an Account instance from a dictionary."""

        timestamp = datetime.fromisoformat(data["created_at"])

        instance = cls(
            id=data["id"],
            acc_name=data["acc_name"],
            acc_type=data["acc_type"],
            created_at=timestamp,
        )

        if "acc_status" in data:
            status = data["acc_status"]

            allowed_statuses = {
                account_status.value for account_status in AccStat
            }

            if status not in allowed_statuses:
                raise StorageCorruptedError(
                    f"Invalid stored account status: '{status}'."
                )

            instance._acc_status = status

        return instance

    def to_dict(self) -> AccDict:
        """Converts the Account instance into a serializable dictionary."""

        return {
            "id": self.id,
            "acc_name": self.acc_name,
            "acc_type": self.acc_type,
            "acc_status": self.acc_status,
            "created_at": self.created_at.isoformat(),
        }
