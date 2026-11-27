
"""Type definitions for Finance Tracker application data structures."""

from __future__ import annotations

from typing import TYPE_CHECKING, NotRequired, TypedDict

if TYPE_CHECKING:
    from models.account import Account
    from models.transaction import Transaction


class WalletEngineData(TypedDict):
    """In-memory application state."""

    accounts: dict[str, Account]
    transactions: list[Transaction]


class TrxDict(TypedDict):
    """Serialized representation of a financial transaction."""

    id: str
    amount: int
    transaction_date: str
    transaction_type: str

    category: NotRequired[str | None]
    desc: NotRequired[str | None]
    source_acc_id: NotRequired[str | None]
    target_acc_id: NotRequired[str | None]


class AccDict(TypedDict):
    """Serialized representation of an account."""

    id: str
    acc_name: str
    acc_type: str
    acc_status: str
    created_at: str


class FundedAccDict(TypedDict):
    """UI display representation of an account with a calculated balance.

    acc_bal is supplied by the Business Logic Layer for display only.
    It is not an Account attribute and must never be persisted.
    """

    id: str
    acc_name: str
    acc_type: str
    acc_bal: int
    acc_status: str
    created_at: str


class JSONData(TypedDict):
    """Serialized JSON storage structure."""

    accounts: dict[str, AccDict]
    transactions: list[TrxDict]
