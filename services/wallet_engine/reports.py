"""Financial reporting operations for the wallet engine."""

from models.transaction import Transaction
from models.enums import TrxType
from models.types import WalletEngineData

from .accounts import get_account
from .ledger import get_account_transactions

from exceptions.errors import DataIntegrityError


def _build_report(
    transactions: list[Transaction],
) -> tuple[int, int, int, dict[str, int]]:
    """Build a financial summary from a transaction collection."""

    total_income = sum(
        transaction.amount
        for transaction in transactions
        if transaction.transaction_type == TrxType.INCOME
    )

    total_expense = sum(
        transaction.amount
        for transaction in transactions
        if transaction.transaction_type == TrxType.EXPENSE
    )

    net_delta = total_income - total_expense

    expenses_by_category: dict[str, int] = {}

    for transaction in transactions:
        if transaction.transaction_type != TrxType.EXPENSE:
            continue

        if transaction.category is None:
            raise DataIntegrityError(
                f"Expense transaction '{transaction.id}' "
                "has no category."
            )

        category = transaction.category.value

        expenses_by_category[category] = (
            expenses_by_category.get(category, 0)
            + transaction.amount
        )

    return (
        total_income,
        total_expense,
        net_delta,
        expenses_by_category,
    )


def get_reports(
    data: WalletEngineData,
) -> tuple[int, int, int, dict[str, int]]:
    """Generate an overall financial summary."""

    return _build_report(data["transactions"])


def get_account_reports(
    data: WalletEngineData,
    acc_id: str,
) -> tuple[int, int, int, dict[str, int]]:
    """Generate a financial summary for one account."""

    get_account(data, acc_id)

    account_transactions = get_account_transactions(
        data["transactions"],
        acc_id,
    )

    return _build_report(account_transactions)