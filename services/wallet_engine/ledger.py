"""Ledger calculations and chronological balance validation."""

from models.account import Account
from models.transaction import Transaction
from models.enums import TrxType

from exceptions.errors import (
    EntityNotFoundError,
    InsufficientFundsError,
)


def calculate_account_balance(
    transactions: list[Transaction],
    account_id: str,
) -> int:
    """Calculate an account's current balance from its transaction history."""

    balance = 0

    for transaction in transactions:

        if transaction.transaction_type == TrxType.INCOME:
            if transaction.target_acc_id == account_id:
                balance += transaction.amount

        elif transaction.transaction_type == TrxType.EXPENSE:
            if transaction.source_acc_id == account_id:
                balance -= transaction.amount

        elif transaction.transaction_type == TrxType.TRANSFER:
            if transaction.source_acc_id == account_id:
                balance -= transaction.amount

            if transaction.target_acc_id == account_id:
                balance += transaction.amount

    return balance


def get_account_transactions(
    transactions: list[Transaction],
    account_id: str,
) -> list[Transaction]:
    """Return transactions involving the specified account."""

    return [
        transaction
        for transaction in transactions
        if (
            transaction.source_acc_id == account_id
            or transaction.target_acc_id == account_id
        )
    ]


def calculate_chronological_balances(
    transactions: list[Transaction],
    accounts: dict[str, Account],
) -> dict[str, int]:
    """Calculate final balances while ensuring no account goes negative
    at any point in chronological transaction history.

    Transactions sharing the same financial date retain their original
    insertion order because Python's sorting algorithm is stable.
    """

    ordered_transactions = sorted(
        transactions,
        key=lambda transaction: transaction.transaction_date,
    )

    balances = {
        account_id: 0
        for account_id in accounts
    }

    for transaction in ordered_transactions:

        if transaction.transaction_type == TrxType.INCOME:
            target_id = transaction.target_acc_id

            if target_id is None or target_id not in balances:
                raise EntityNotFoundError(
                    f"Income transaction '{transaction.id}' references "
                    "an unknown target account."
                )

            balances[target_id] += transaction.amount

        elif transaction.transaction_type == TrxType.EXPENSE:
            source_id = transaction.source_acc_id

            if source_id is None or source_id not in balances:
                raise EntityNotFoundError(
                    f"Expense transaction '{transaction.id}' references "
                    "an unknown source account."
                )

            balances[source_id] -= transaction.amount

            if balances[source_id] < 0:
                raise InsufficientFundsError(
                    f"Transaction '{transaction.id}' creates a negative "
                    f"historical balance for account '{source_id}'."
                )

        elif transaction.transaction_type == TrxType.TRANSFER:
            source_id = transaction.source_acc_id
            target_id = transaction.target_acc_id

            if (
                source_id is None
                or target_id is None
                or source_id not in balances
                or target_id not in balances
            ):
                raise EntityNotFoundError(
                    f"Transfer '{transaction.id}' references "
                    "an unknown account."
                )

            balances[source_id] -= transaction.amount

            if balances[source_id] < 0:
                raise InsufficientFundsError(
                    f"Transfer '{transaction.id}' creates a negative "
                    f"historical balance for account '{source_id}'."
                )

            balances[target_id] += transaction.amount

    return balances