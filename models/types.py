
from __future__ import annotations

from typing import TypedDict, TYPE_CHECKING, NotRequired

if TYPE_CHECKING:
    from models.account import Account
    from models.transaction import Transaction


class WalletEngineData(TypedDict):
    accounts: dict[str, Account]
    transactions: list[Transaction]


class TrxDict(TypedDict):
    """Serialization schema for application transactions."""

    id: str
    amount: int
    transaction_date: str
    transaction_type: str

    category: NotRequired[str | None]
    desc: NotRequired[str | None]
    source_acc_id: NotRequired[str | None]
    target_acc_id: NotRequired[str | None]
    reverses_transaction_id: NotRequired[str | None]


class AccDict(TypedDict):
    """Serialization schema for individual accounts."""

    id: str
    acc_name: str
    acc_type: str
    acc_status: str
    created_at: str


class JSONData(TypedDict):
    """Serialized storage map matching the final output JSON structure."""

    accounts: dict[str, AccDict]
    transactions: list[TrxDict]