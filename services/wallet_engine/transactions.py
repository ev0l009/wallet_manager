"""Financial transaction operations for the wallet engine."""

from models.transaction import Transaction
from models.enums import TrxType, ExpCatOpts
from models.types import WalletEngineData

from utils.validators import (
    convert_to_kobo,
    get_valid_date,
)

from exceptions.errors import (
    EntityNotFoundError,
    InvalidCategoryError,
)

from services.wallet_engine.accounts import get_active_account

from services.wallet_engine.identifiers import (
    generate_id,
    TRX_ID_PREFIX,
)

from services.wallet_engine.ledger import (
    calculate_chronological_balances,
)


def record_income(
    data: WalletEngineData,
    acc_id: str,
    amount: str,
    desc: str,
    inp_date: str,
) -> tuple[WalletEngineData, Transaction]:
    """Record income into an account."""

    get_active_account(data, acc_id)

    transaction = Transaction(
        id=generate_id(TRX_ID_PREFIX, data),
        amount=convert_to_kobo(amount),
        target_acc_id=acc_id,
        desc=desc,
        transaction_date=get_valid_date(inp_date),
        transaction_type=TrxType.INCOME,
    )

    proposed_transactions = [
        *data["transactions"],
        transaction,
    ]

    calculate_chronological_balances(
        proposed_transactions,
        data["accounts"],
    )

    proposed_data: WalletEngineData = {
        "accounts": dict(data["accounts"]),
        "transactions": proposed_transactions,
    }

    return proposed_data, transaction


def record_expense(
    data: WalletEngineData,
    acc_id: str,
    amount: str,
    exp_cat: str,
    desc: str,
    inp_date: str,
) -> tuple[WalletEngineData, Transaction]:
    """Record an expense from an account."""

    get_active_account(data, acc_id)

    try:
        category = ExpCatOpts(exp_cat)
    except (TypeError, ValueError) as exc:
        raise InvalidCategoryError(
            f"Unsupported expense category: '{exp_cat}'."
        ) from exc

    transaction = Transaction(
        id=generate_id(TRX_ID_PREFIX, data),
        amount=convert_to_kobo(amount),
        category=category,
        source_acc_id=acc_id,
        desc=desc,
        transaction_date=get_valid_date(inp_date),
        transaction_type=TrxType.EXPENSE,
    )

    proposed_transactions = [
        *data["transactions"],
        transaction,
    ]

    calculate_chronological_balances(
        proposed_transactions,
        data["accounts"],
    )

    proposed_data: WalletEngineData = {
        "accounts": dict(data["accounts"]),
        "transactions": proposed_transactions,
    }

    return proposed_data, transaction


def record_transfer(
    data: WalletEngineData,
    source_acc_id: str,
    amount: str,
    target_acc_id: str,
    inp_date: str,
) -> tuple[WalletEngineData, Transaction]:
    """Transfer funds between two accounts."""

    get_active_account(data, source_acc_id)
    get_active_account(data, target_acc_id)

    transaction = Transaction(
        id=generate_id(TRX_ID_PREFIX, data),
        amount=convert_to_kobo(amount),
        source_acc_id=source_acc_id,
        target_acc_id=target_acc_id,
        transaction_date=get_valid_date(inp_date),
        transaction_type=TrxType.TRANSFER,
    )

    proposed_transactions = [
        *data["transactions"],
        transaction,
    ]

    calculate_chronological_balances(
        proposed_transactions,
        data["accounts"],
    )

    proposed_data: WalletEngineData = {
        "accounts": dict(data["accounts"]),
        "transactions": proposed_transactions,
    }

    return proposed_data, transaction


def get_transaction(
    data: WalletEngineData,
    trx_id: str,
) -> Transaction:
    """Retrieve a transaction by ID."""

    for transaction in data["transactions"]:
        if transaction.id == trx_id:
            return transaction

    raise EntityNotFoundError(
        f"Transaction '{trx_id}' does not exist."
    )


def get_transactions(
    data: WalletEngineData,
) -> list[Transaction]:
    """Return the complete transaction history."""

    return list(data["transactions"])