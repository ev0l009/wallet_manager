"""Account management operations for the wallet engine."""

from datetime import datetime, timezone

from models.account import Account
from models.enums import AccStat, AccType
from models.types import WalletEngineData

from exceptions.errors import (
    AccountBalanceNotZeroError,
    DuplicateAccountNameError,
    EntityNotFoundError,
    InactiveAccountError,
    InvalidAccountNameError,
    InvalidAccountTypeError,
)

from services.wallet_engine.identifiers import (
    generate_id,
    ACC_ID_PREFIX,
)


def create_account(
    data: WalletEngineData,
    acc_name: str,
    acc_type: str,
) -> tuple[WalletEngineData, Account]:
    """Create an account and return the proposed application state."""

    if not isinstance(acc_name, str):
        raise InvalidAccountNameError(
            "Account name must be a string."
        )

    normalized_name = acc_name.strip().casefold()

    for account in data["accounts"].values():
        if account.acc_name.casefold() == normalized_name:
            raise DuplicateAccountNameError(
                f"An account named '{acc_name}' already exists."
            )

    try:
        account_type = AccType(acc_type)
    except (TypeError, ValueError) as exc:
        raise InvalidAccountTypeError(
            f"Unsupported account type: '{acc_type}'."
        ) from exc

    account = Account(
        id=generate_id(ACC_ID_PREFIX, data),
        acc_name=acc_name,
        acc_type=account_type,
        created_at=datetime.now(timezone.utc),
    )

    proposed_data: WalletEngineData = {
        "accounts": {
            **data["accounts"],
            account.id: account,
        },
        "transactions": list(data["transactions"]),
    }

    return proposed_data, account


def rename_account(
    data: WalletEngineData,
    acc_id: str,
    acc_name: str,
) -> tuple[WalletEngineData, Account]:
    """Rename an account and return the proposed application state."""

    account = get_account(data, acc_id)

    if not isinstance(acc_name, str):
        raise InvalidAccountNameError(
            "Account name must be a string."
        )

    normalized_name = acc_name.strip().casefold()

    for other_account in data["accounts"].values():
        if other_account.id == acc_id:
            continue

        if other_account.acc_name.casefold() == normalized_name:
            raise DuplicateAccountNameError(
                f"An account named '{acc_name}' already exists."
            )

    updated_account = account.rename(acc_name)

    proposed_data: WalletEngineData = {
        "accounts": {
            **data["accounts"],
            acc_id: updated_account,
        },
        "transactions": list(data["transactions"]),
    }

    return proposed_data, updated_account


def get_account(
    data: WalletEngineData,
    acc_id: str,
) -> Account:
    """Retrieve an account by ID."""

    account = data["accounts"].get(acc_id)

    if account is None:
        raise EntityNotFoundError(
            f"Account '{acc_id}' does not exist."
        )

    return account


def get_active_account(
    data: WalletEngineData,
    acc_id: str,
) -> Account:
    """Retrieve an account and ensure it is active."""

    account = get_account(data, acc_id)

    if account.acc_status != AccStat.ACTIVE:
        raise InactiveAccountError(
            f"Account '{acc_id}' is inactive."
        )

    return account


def get_active_accounts(
    data: WalletEngineData,
) -> list[Account]:
    """Return all active accounts."""

    return [
        account
        for account in data["accounts"].values()
        if account.acc_status == AccStat.ACTIVE
    ]


def get_inactive_accounts(
    data: WalletEngineData,
) -> list[Account]:
    """Return all inactive accounts."""

    return [
        account
        for account in data["accounts"].values()
        if account.acc_status == AccStat.INACTIVE
    ]


def get_all_accounts(
    data: WalletEngineData,
) -> list[Account]:
    """Return all accounts."""

    return list(data["accounts"].values())


def get_all_account_map(
    data: WalletEngineData,
) -> dict[str, str]:
    """Return all account IDs mapped to account names."""

    return {
        account.id: account.acc_name
        for account in get_all_accounts(data)
    }


def get_active_account_map(
    data: WalletEngineData,
) -> dict[str, str]:
    """Return active account IDs mapped to account names."""

    return {
        account.id: account.acc_name
        for account in get_active_accounts(data)
    }


def get_inactive_account_map(
    data: WalletEngineData,
) -> dict[str, str]:
    """Return inactive account IDs mapped to account names."""

    return {
        account.id: account.acc_name
        for account in get_inactive_accounts(data)
    }


def reactivate_account(
    data: WalletEngineData,
    acc_id: str,
) -> tuple[WalletEngineData, Account]:
    """Reactivate an inactive account."""

    account = get_account(data, acc_id)
    updated_account = account.reactivate()

    proposed_data: WalletEngineData = {
        "accounts": {
            **data["accounts"],
            acc_id: updated_account,
        },
        "transactions": list(data["transactions"]),
    }

    return proposed_data, updated_account


def deactivate_account(
    data: WalletEngineData,
    acc_id: str,
    balance: int,
) -> tuple[WalletEngineData, Account]:
    """Deactivate an active account with a zero balance."""

    account = get_active_account(data, acc_id)

    if balance != 0:
        raise AccountBalanceNotZeroError(
            "An account must have a zero balance before deactivation."
        )

    updated_account = account.deactivate()

    proposed_data: WalletEngineData = {
        "accounts": {
            **data["accounts"],
            acc_id: updated_account,
        },
        "transactions": list(data["transactions"]),
    }

    return proposed_data, updated_account