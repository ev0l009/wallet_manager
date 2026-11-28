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
    TransactionCapacityExceededError,
)

from .accounts import get_active_account

from .identifiers import (
    generate_id,
    TRX_ID_PREFIX,
)

from .ledger import (
    calculate_chronological_balances,
)


# Transaction capacity thresholds.
TRANSACTION_WARNING_THRESHOLD = 4_000
TRANSACTION_REASSESSMENT_THRESHOLD = 5_000
MAX_TRANSACTIONS = 10_000


def _check_transaction_capacity(data: WalletEngineData) -> None:
    """Reject new transactions when the absolute capacity is reached."""

    if len(data["transactions"]) >= MAX_TRANSACTIONS:
        raise TransactionCapacityExceededError(
            f"The transaction limit of {MAX_TRANSACTIONS:,} "
            "has been reached. No additional transactions can be recorded."
        )


def get_transaction_capacity_warning(
    data: WalletEngineData,
) -> str | None:
    """Return the applicable transaction capacity warning, if any."""

    transaction_count = len(data["transactions"])

    if transaction_count >= MAX_TRANSACTIONS:
        return (
            f"The maximum transaction capacity of {MAX_TRANSACTIONS:,} "
            "has been reached."
        )

    if transaction_count >= TRANSACTION_REASSESSMENT_THRESHOLD:
        return (
            f"The application contains {transaction_count:,} transactions. "
            "Reassess the application architecture and storage approach."
        )

    if transaction_count >= TRANSACTION_WARNING_THRESHOLD:
        return (
            f"The application contains {transaction_count:,} transactions. "
            "The operational capacity warning threshold has been reached."
        )

    return None


def record_income(
    data: WalletEngineData,
    acc_id: str,
    amount: str,
    desc: str,
    inp_date: str,
) -> tuple[WalletEngineData, Transaction]:
    """Record income into an account."""

    _check_transaction_capacity(data)
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

    _check_transaction_capacity(data)
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

    _check_transaction_capacity(data)
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