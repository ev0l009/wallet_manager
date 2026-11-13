from __future__ import annotations
from typing import TypedDict, TYPE_CHECKING

from datetime import date

if TYPE_CHECKING:
    from models.account import Account
    from models.transaction import Transaction

class WalletEngineData(TypedDict):
    accounts: dict [str, Account ]
    transactions: list [ Transaction ]

class TrxDict(TypedDict):
    """Base serialization schema for all application transactions."""

    id: str
    amount: int
    transaction_date: date