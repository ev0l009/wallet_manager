"""Presentation handlers for wallet operations.

Collects user input, delegates business operations to WalletEngine,
and passes resulting data to the presentation views.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from exceptions.errors import WalletError

from models.types import FundedAccDict

from ui.menu_states import AccDashState

from ui.menus import (
    select_acc,
    get_acc_dash_state,
    get_exp_category,
    get_acc_type,
)

from ui.views import (
    display_active_accounts,
    display_acc_bal,
    display_reports,
    display_transactions,
    display_account_details,
)

from utils.validators import get_valid_acc_name


if TYPE_CHECKING:
    from services.wallet_engine.engine import WalletEngine
    from models.account import Account


def create_account(wallet_instance: WalletEngine) -> None:
    """Collect account details and create a new account."""

    acc_type = get_acc_type()

    if not acc_type:
        return

    raw_name = input("  Enter account name → ")

    try:
        all_acc_map = wallet_instance.get_all_acc_map()

        acc_name = get_valid_acc_name(
            raw_name,
            all_acc_map,
        )

        wallet_instance.create_account(
            acc_name,
            acc_type,
        )

    except WalletError as err:
        print(err)

    else:
        print("\n  [✓] Account created successfully.")


def record_transfer(
    wallet_instance: WalletEngine,
    acc_map: dict[str, str],
) -> None:
    """Collect transfer details and record a transfer."""

    source_acc_id = select_acc(
        acc_map,
        heading="SELECT SOURCE ACCOUNT",
    )

    if source_acc_id is None:
        return

    target_acc_id = select_acc(
        acc_map=acc_map,
        id_to_skip=source_acc_id,
        heading="SELECT DESTINATION ACCOUNT",
    )

    if target_acc_id is None:
        return

    try:
        raw_amt = input("Enter amount: ").strip()
        raw_date = input(
            "Enter transaction date [YYYY-MM-DD]: "
        ).strip()

        wallet_instance.record_transfer(
            source_acc_id=source_acc_id,
            inp_amt=raw_amt,
            target_acc_id=target_acc_id,
            inp_date=raw_date,
        )

    except WalletError as err:
        print(err)

    else:
        print("\n  [✓] Transfer record successful.")


def record_income(
    wallet_instance: WalletEngine,
    acc_id: str,
) -> None:
    """Collect income details and record an income transaction."""

    try:
        raw_amt = input("Enter amount: ").strip()
        raw_date = input(
            "Enter transaction date [YYYY-MM-DD]: "
        ).strip()
        desc = input("Enter a short description: ").strip()

        wallet_instance.record_income(
            acc_id=acc_id,
            amount=raw_amt,
            desc=desc,
            inp_date=raw_date,
        )

    except WalletError as err:
        print(err)

    else:
        print("\n  [✓] Income record successful.")


def record_expense(
    wallet_instance: WalletEngine,
    acc_id: str,
) -> None:
    """Collect expense details and record an expense transaction."""

    raw_amt = input("Enter amount: ").strip()

    exp_cat = get_exp_category()

    if not exp_cat:
        return

    desc = input("Enter a short description: ").strip()
    raw_date = input(
        "Enter transaction date [YYYY-MM-DD]: "
    ).strip()

    try:
        wallet_instance.record_expense(
            acc_id=acc_id,
            amount=raw_amt,
            exp_cat=exp_cat,
            desc=desc,
            inp_date=raw_date,
        )

    except WalletError as err:
        print(err)

    else:
        print("\n  [✓] Expense record successful.")


def manage_account(wallet_instance: WalletEngine) -> None:
    """Manage and inspect an individual account."""

    acc_map = wallet_instance.get_all_acc_map()

    selected_acc_id = select_acc(acc_map)

    if selected_acc_id is None:
        return

    acc = wallet_instance.get_account(selected_acc_id)

    acc_dash_state = AccDashState.ACC_DASH

    while True:

        if acc_dash_state == AccDashState.ACC_DASH:
            acc_dash_state = get_acc_dash_state(acc.acc_name)

        elif acc_dash_state == AccDashState.BALANCE:
            acc_bal = wallet_instance.get_acc_bal(acc.id)

            display_acc_bal(acc_bal)

            acc_dash_state = AccDashState.ACC_DASH

        elif acc_dash_state == AccDashState.DEPOSIT:
            record_income(wallet_instance, acc.id)

            acc_dash_state = AccDashState.ACC_DASH

        elif acc_dash_state == AccDashState.WITHDRAWAL:
            record_expense(wallet_instance, acc.id)

            acc_dash_state = AccDashState.ACC_DASH

        elif acc_dash_state == AccDashState.UPDATE_ACC:
            updated_acc = update_account_name(
                wallet_instance,
                acc,
            )

            if updated_acc is not None:
                acc = updated_acc

            acc_dash_state = AccDashState.ACC_DASH

        elif acc_dash_state == AccDashState.ACCOUNT_TRANSACTIONS:
            acc_transactions = wallet_instance.get_acc_transactions(
                acc.id
            )

            display_transactions(acc_transactions)

            acc_dash_state = AccDashState.ACC_DASH

        elif acc_dash_state == AccDashState.ACCOUNT_INFO:
            acc_with_bal: FundedAccDict = {
                **acc.to_dict(),
                "acc_bal": wallet_instance.get_acc_bal(acc.id),
            }

            display_account_details(acc_with_bal)

            acc_dash_state = AccDashState.ACC_DASH

        elif acc_dash_state == AccDashState.ACCOUNT_REPORTS:
            show_account_reports(
                acc.id,
                wallet_instance,
            )

            acc_dash_state = AccDashState.ACC_DASH

        elif acc_dash_state == AccDashState.DEACTIVATE:
            try:
                wallet_instance.deactivate_acc(acc.id)

            except WalletError as err:
                print(err)

                acc_dash_state = AccDashState.ACC_DASH

            else:
                print("\n  [✓] Account deactivated successfully.")
                break

        elif acc_dash_state == AccDashState.RETURN:
            break

        else:
            print("Invalid selection. Try again.")

            acc_dash_state = AccDashState.ACC_DASH


def show_active_accounts(wallet_instance: WalletEngine) -> None:
    """Display active accounts with their calculated balances."""

    active_accounts = wallet_instance.get_active_accounts()

    funded_active_accounts: list[FundedAccDict] = [
        {
            **acc.to_dict(),
            "acc_bal": wallet_instance.get_acc_bal(acc.id),
        }
        for acc in active_accounts
    ]

    display_active_accounts(funded_active_accounts)


def show_reports(wallet_instance: WalletEngine) -> None:
    """Generate and display the overall financial report."""

    (
        total_income,
        total_expense,
        net_delta,
        expenses_by_category,
    ) = wallet_instance.get_reports()

    display_reports(
        total_income,
        total_expense,
        net_delta,
        expenses_by_category,
    )


def show_account_reports(
    acc_id: str,
    wallet_instance: WalletEngine,
) -> None:
    """Generate and display a report for an individual account."""

    (
        total_income,
        total_expense,
        net_delta,
        expenses_by_category,
    ) = wallet_instance.get_account_reports(acc_id)

    display_reports(
        total_income,
        total_expense,
        net_delta,
        expenses_by_category,
    )


def update_account_name(
    wallet_instance: WalletEngine,
    acc_instance: Account,
) -> Account | None:
    """Collect and validate a new account name."""

    new_acc_name = input("Enter the new account name: ").strip()

    try:
        all_acc_map = wallet_instance.get_all_acc_map()

        # Exclude the account being renamed from duplicate checking.
        other_accounts = {
            acc_id: acc_name
            for acc_id, acc_name in all_acc_map.items()
            if acc_id != acc_instance.id
        }

        cleaned_name = get_valid_acc_name(
            new_acc_name,
            other_accounts,
        )

        updated_account = wallet_instance.update_account_name(
            acc_instance.id,
            cleaned_name,
        )

    except WalletError as err:
        print(err)
        return None

    print("\n  [✓] Account updated successfully.")

    return updated_account