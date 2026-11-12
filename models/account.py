"""Account domain models for the Finance Tracker application.

Defines the core operational Account entity, ensuring strict maintenance of 
financial invariants, lifecycle state machines, and safe JSON serialization.
"""

from datetime import datetime, timezone

from exceptions.errors import (
    EntityNotFoundError,
    InvalidAccountNameError,
    InvalidAccountTypeError
)

class Account:
    """Encapsulates account configurations, state constraints, and balance updates.""" 

    def __init__(
        self,
        id: str,
        acc_name: str,
        acc_type: str,
        amount: int,
        created_at: datetime | str | None = None,
    ):
        if not id or not id.strip():
            raise EntityNotFoundError("Account ID cannot be empty.")
        self._id = id

        if not acc_name.strip():
            raise InvalidAccountNameError("Account name cannot be empty.")
        if len(acc_name.strip()) < 3:
            raise InvalidAccountNameError("Account name cannot be less three characters.")
        self.acc_name = acc_name

        allowed_types = {t.value for t in AccType}
        if acc_type not in allowed_types:
            raise InvalidAccountTypeError(f"Invalid account type '{acc_type}'. Must be one of {allowed_types}")
        self._acc_type = acc_type

        if isinstance(created_at, str):
            self._created_at = datetime.fromisoformat(created_at)
        else:
            self._created_at = created_at if created_at else datetime.now(timezone.utc).replace(microsecond=0)

        self.balance = amount  
        self._acc_status = AccStat.ACTIVE.value