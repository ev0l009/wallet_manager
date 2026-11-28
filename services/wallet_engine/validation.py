"""Application data integrity validation."""

from models.types import WalletEngineData

from .ledger import (
    calculate_chronological_balances,
)

from exceptions.errors import (
    DataIntegrityError,
    InsufficientFundsError,
    NegativeBalanceError,
)


def validate_loaded_data(data: WalletEngineData) -> None:
    """Validate cross-entity references and financial consistency."""

    accounts = data["accounts"]
    transactions = data["transactions"]

    # Validate account dictionary keys and account-name uniqueness.
    account_names: set[str] = set()

    for account_id, account in accounts.items():

        if account_id != account.id:
            raise DataIntegrityError(
                f"Account dictionary key '{account_id}' does not match "
                f"account ID '{account.id}'."
            )

        normalized_name = account.acc_name.casefold()

        if normalized_name in account_names:
            raise DataIntegrityError(
                f"Duplicate account name: '{account.acc_name}'."
            )

        account_names.add(normalized_name)

    # Validate transaction IDs and account references.
    transaction_ids: set[str] = set()

    for transaction in transactions:

        if transaction.id in transaction_ids:
            raise DataIntegrityError(
                f"Duplicate transaction ID: '{transaction.id}'."
            )

        transaction_ids.add(transaction.id)

        referenced_account_ids = {
            transaction.source_acc_id,
            transaction.target_acc_id,
        } - {None}

        for account_id in referenced_account_ids:
            if account_id not in accounts:
                raise DataIntegrityError(
                    f"Transaction '{transaction.id}' references "
                    f"unknown account '{account_id}'."
                )

    # Validate chronological financial consistency.
    try:
        calculate_chronological_balances(
            transactions,
            accounts,
        )

    except InsufficientFundsError as exc:
        raise NegativeBalanceError(
            "Transaction history produces a negative "
            "historical account balance."
        ) from exc