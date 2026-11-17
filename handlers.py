from __future__ import annotations
from typing import TYPE_CHECKING

from ui.menus import (
    get_acc_type, 
    select_acc,
    get_exp_category
)

from utils.validators import (
    get_valid_acc_name,
)

from exceptions.errors import (
    WalletError
)

if TYPE_CHECKING:
    from services.wallet_engine import WalletEngine

def create_account(
    wallet_instance: WalletEngine, 
    acc_map: dict[str, str]
):
    raw_name = input("  Enter account name → ")
    acc_type = get_acc_type()

    if acc_type:
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
):
    source_acc_id = select_acc(acc_map)
    target_acc_id = select_acc(
        acc_map=acc_map, 
        id_to_skip=source_acc_id
    )

    if source_acc_id and target_acc_id:
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
):
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
):
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