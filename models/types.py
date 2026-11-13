from __future__ import annotations
from typing import TypedDict, TYPE_CHECKING

from datetime import date

if TYPE_CHECKING:
    from models.account import Account
    from models.transaction import Transaction, TransferTrx

class WalletEngineData(TypedDict):
    accounts: dict [str, Account ]
    transactions: list [ Transaction | TransferTrx ]

class TrxDict(TypedDict):
    """Base serialization schema for all application transactions."""

    id: str
    amount: int
    transaction_date: date


class TransferTrxDict(TrxDict):
    """Serialization schema for peer-to-peer account transfers."""

    source_acc_id: str
    target_acc_id: str
    transaction_type: str