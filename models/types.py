from __future__ import annotations
from typing import TypedDict, TYPE_CHECKING
from enum import Enum

if TYPE_CHECKING:
    from models.account import Account
    from models.transaction import Transaction

class WalletEngineData(TypedDict):
    accounts: dict [str, Account ]
    transactions: list [ Transaction ]

class AccType(Enum):
    """Supported underlying storage classification for accounts."""

    BANK = "bank"
    CASH = "cash"
    SAVINGS = "savings"
    MOBILE = "mobile"

class AccStat(Enum):
    """Lifecycle states for operational accounts."""

    ACTIVE = "active"
    INACTIVE = "inactive"

class TrxDict(TypedDict):
    """Base serialization schema for all application transactions."""

    id: str
    amount: int
    transaction_date: str