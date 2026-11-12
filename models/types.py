from __future__ import annotations
from typing import TypedDict, TYPE_CHECKING

if TYPE_CHECKING:
    from models.account import Account
    from models.transaction import Transaction

class WalletEngineData(TypedDict):
    accounts: dict [str, Account ]
    transactions: list [ Transaction ]