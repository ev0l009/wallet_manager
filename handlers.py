from __future__ import annotations
from typing import TYPE_CHECKING

from utils.validators import (
    get_valid_acc_name,
)

from exceptions.errors import (
    WalletError
)

from ui.views import (
    display_active_accounts,
    display_acc_bal,
    display_reports,
    display_transactions,
    display_account_details
)

from ui.menus import (
    select_acc,
    get_acc_dash_state,
    get_exp_category,
    get_acc_type
)

from utils.validators import get_valid_acc_name

from ui.menu_states import AccDashState

from models.types import FundedAccDict

if TYPE_CHECKING:
    from services.wallet_engine import WalletEngine
    from models.account import Account

def create_account(
    wallet_instance: WalletEngine, 
    acc_map: dict[str, str]
) -> None:
    acc_type = get_acc_type()

    if not acc_type:
        return
    
    raw_name = input("  Enter account name → ")

    try:
        acc_name = get_valid_acc_name(raw_name, acc_map)
        wallet_instance.create_account(acc_name,acc_type)
    except WalletError as err:
        print(err)
    else:
        print("\n  [✓] Account created successfully.")


def record_transfer(
    wallet_instance: WalletEngine, 
    acc_map: dict[str, str]
) -> None:
    source_acc_id = select_acc(acc_map)
    if source_acc_id is None:
        return
    
    target_acc_id = select_acc(
        acc_map=acc_map, 
        id_to_skip=source_acc_id
    )
    if target_acc_id is None:
        return

    try:
        raw_amt = input("Enter amount: ").strip()
        raw_date = input("Enter transaction date [YYYY-MM-DD]: ").strip()

        wallet_instance.record_transfer(
            source_acc_id=source_acc_id,
            target_acc_id=target_acc_id,
            inp_amt=raw_amt,
            inp_date=raw_date
        )
    except WalletError as err:
        print(err)
    else:
        print("\n  [✓] Transfer record successful.")

def record_income(
    wallet_instance: WalletEngine, 
    acc_id: str
) -> None:
    try:
        raw_amt = input("Enter amount: ").strip()
        raw_date = input("Enter transaction date [YYYY-MM-DD]: ").strip()
        desc = input("Enter a short description: ").strip()
        wallet_instance.record_income(
            acc_id=acc_id,
            amount=raw_amt,
            desc=desc,
            inp_date=raw_date
        )
    except WalletError as err:
        print(err)
    else:
        print("\n  [✓] Income record successful.")


def record_expense(
    wallet_instance: WalletEngine, 
    acc_id: str
) -> None:
    raw_amt = input("Enter amount: ").strip()

    exp_cat = get_exp_category()

    if exp_cat:
        desc = input("Enter a short description: ").strip()
        raw_date = input("Enter transaction date [YYYY-MM-DD]: ").strip()
        try:
            wallet_instance.record_expense(
                acc_id=acc_id,
                amount=raw_amt,
                exp_cat=exp_cat,
                desc=desc,
                inp_date=raw_date
            )
        except WalletError as err:
            print(err)
        else:
            print("\n  [✓] Expense record successful.")


def record_reversal(wallet_instance: WalletEngine) -> None:
    original_trx_id = input("Enter the original transaction ID: ").strip()
    raw_date = input("Enter transaction date [YYYY-MM-DD]: ").strip()

    try:
        wallet_instance.record_reversal(
            original_trx_id=original_trx_id,
            inp_date=raw_date
        )
    except WalletError as err:
        print(err)
    else:
        print("\n  [✓] Transaction reversal successful.")


def manage_account(wallet_instance: WalletEngine) -> None:
    acc_map = wallet_instance.get_all_acc_map()
            
    selected_acc_id = select_acc(acc_map)

    if selected_acc_id:

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
                
                record_income( wallet_instance, acc.id)
                acc_dash_state = AccDashState.ACC_DASH

            elif acc_dash_state == AccDashState.WITHDRAWAL:
                record_expense( wallet_instance, acc.id )
                acc_dash_state = AccDashState.ACC_DASH

            elif acc_dash_state == AccDashState.UPDATE_ACC:
                update_account_name( wallet_instance, acc, acc_map )
                acc_dash_state = AccDashState.ACC_DASH

            elif acc_dash_state == AccDashState.ACCOUNT_TRANSACTIONS:
                acc_transactions = wallet_instance.get_acc_transactions(acc.id)
                display_transactions(acc_transactions)
                acc_dash_state = AccDashState.ACC_DASH

            elif acc_dash_state == AccDashState.ACCOUNT_INFO:
                acc_with_bal: FundedAccDict = {
                    **acc.to_dict(),
                    "acc_bal": wallet_instance.get_acc_bal(acc.id)
                }
                display_account_details(acc_with_bal)
                acc_dash_state = AccDashState.ACC_DASH

            elif acc_dash_state == AccDashState.ACCOUNT_REPORTS:
                print(acc)
                acc_dash_state = AccDashState.ACC_DASH

            elif acc_dash_state == AccDashState.DEACTIVATE:
                try:
                    wallet_instance.deactivate_acc(acc.id)
                except WalletError as err:
                    print(err)
                else:
                    print("\n  [✓] Account deactivated successfully.")

                break

            # activity/summary(overview of transaction by account, expense by category etc)

            elif acc_dash_state == AccDashState.RETURN:
                break

            else:
                print("Invalid selection. try again...")
                acc_dash_state = AccDashState.ACC_DASH

def show_active_accounts(wallet_instance: WalletEngine) -> None:
    active_accounts = wallet_instance.get_active_accounts()
    funded_active_accounts: list[FundedAccDict] = [
        {
            **acc.to_dict(), 
            "acc_bal": wallet_instance.get_acc_bal(acc.id)
        }
        for acc in active_accounts
    ]
    
    display_active_accounts(funded_active_accounts)


def show_reports(wallet_instance: WalletEngine) -> None:
    (
        total_income, 
        total_expense, 
        net_delta, 
        expenses_by_category
    ) = wallet_instance.get_reports()

    display_reports(
        total_income, 
        total_expense, 
        net_delta, 
        expenses_by_category
    )

def update_account_name(
    wallet_instance: WalletEngine, 
    acc_instance: Account,
    acc_map: dict [str, str]
):
    new_acc_name = input("Enter the new Account Name: ").strip()
    try:
        cleaned_name = get_valid_acc_name(new_acc_name, acc_map)
        wallet_instance.update_account_name(
            acc_instance.id,
            cleaned_name
        )
    except WalletError as err:
        print(err)
    else:
        print("\n  [✓] Account updated successfully.")