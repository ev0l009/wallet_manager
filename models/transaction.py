"""Transaction domain models for the Finance Tracker application.

Defines an immutable data layer structure modeling financial transfers, 
deposits, and withdrawals using Python data classes.
"""

from dataclasses import dataclass, field

from exceptions.errors import (
    EntityNotFoundError,
    InvalidAmountError
)

@dataclass(frozen=True, kw_only=True)
class Transaction:
    """Base immutable schema for all financial transaction entities."""
    id: str
    amount: int
    timestamp: datetime | str = field(default_factory=generate_timestamp)

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
            "timestamp": data.get("timestamp") or generate_timestamp(),
        }