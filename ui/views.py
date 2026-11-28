"""Presentation functions for displaying wallet information."""

from __future__ import annotations

from typing import TYPE_CHECKING

from models.enums import TrxType
from models.types import FundedAccDict


if TYPE_CHECKING:
    from models.transaction import Transaction


def format_money(amount_kobo: int) -> str:
    """Format an integer Kobo amount as Nigerian Naira.

    Avoids floating-point conversion to preserve monetary precision.
    """

    sign = "-" if amount_kobo < 0 else ""
    naira, kobo = divmod(abs(amount_kobo), 100)

    return f"{sign}₦{naira:,}.{kobo:02d}"


def display_active_accounts(
    funded_active_accounts: list[FundedAccDict],
) -> None:
    """Display a formatted table of active accounts."""

    print("\n  ACTIVE ACCOUNTS")
    print("  " + "—" * 90)

    if not funded_active_accounts:
        print("  [i] There are no active accounts right now.\n")
        return

    print(
        f"  {'Account Name':<20} "
        f"{'Account ID':<36} "
        f"{'Type':<12} "
        f"{'Balance':>16}"
    )

    print("  " + "—" * 90)

    for acc in funded_active_accounts:
        name = acc["acc_name"].title()

        if len(name) > 20:
            name = name[:17] + "..."

        acc_id = acc["id"]
        type_str = acc["acc_type"].replace("_", " ").title()
        balance_str = format_money(acc["acc_bal"])

        print(
            f"  {name:<20} "
            f"{acc_id:<36} "
            f"{type_str:<12} "
            f"{balance_str:>16}"
        )

    print("  " + "—" * 90 + "\n")


def display_account_details(acc: FundedAccDict) -> None:
    """Display detailed information about an individual account."""

    print("\n  ACCOUNT DETAILS")
    print("  " + "—" * 36)

    print(f"  ID:        {acc['id']}")
    print(f"  Name:      {acc['acc_name'].title()}")
    print(
        f"  Type:      {acc['acc_type'].replace('_', ' ').title()}"
    )
    print(f"  Status:    {acc['acc_status'].upper()}")
    print(f"  Created:   {acc['created_at']}")

    print("  " + "—" * 36)

    print(f"  Balance:   {format_money(acc['acc_bal'])}")

    print("  " + "—" * 36 + "\n")


def display_acc_bal(acc_bal: int) -> None:
    """Display an account balance represented in Kobo."""

    print("\n  CURRENT BALANCE")
    print("  " + "—" * 25)

    print(f"  Available Funds:  {format_money(acc_bal)}")

    print("  " + "—" * 25 + "\n")


def display_transactions(
    transactions: list[Transaction],
) -> None:
    """Display historical financial transactions."""

    if not transactions:
        print("\n  [!] No transactions found in this ledger.\n")
        return

    print("\n  TRANSACTION HISTORY")
    print("  " + "—" * 85)

    print(
        f"  {'ID':<15} "
        f"{'Type':<11} "
        f"{'Amount':>18} "
        f"{'Date':>12}"
    )

    print("  " + "—" * 85)

    for trx in transactions:
        trx_id = trx.id
        trx_type = trx.transaction_type.value.capitalize()
        amount = format_money(trx.amount)

        if trx.transaction_type == TrxType.INCOME:
            amount_str = f"+{amount}"

        elif trx.transaction_type == TrxType.EXPENSE:
            amount_str = f"-{amount}"

        elif trx.transaction_type == TrxType.TRANSFER:
            amount_str = f"⇄ {amount}"

        else:
            amount_str = amount

        date_str = trx.transaction_date.strftime("%Y-%m-%d")

        print(
            f"  {trx_id:<15} "
            f"{trx_type:<11} "
            f"{amount_str:>18} "
            f"{date_str:>12}"
        )

        if trx.desc:
            print(f"      Description: {trx.desc}")

    print("  " + "—" * 85 + "\n")


def display_reports(
    total_income: int,
    total_expense: int,
    net_delta: int,
    expenses_by_category: dict[str, int],
) -> None:
    """Display pre-calculated financial reporting figures.

    All monetary values are represented in Kobo.
    """

    print("\n  FINANCIAL REPORT OVERVIEW")
    print("  " + "—" * 35)

    print(f"  Net Balance Change: {format_money(net_delta)}")
    print(f"  Total Income (+):   {format_money(total_income)}")
    print(f"  Total Expenses (-): {format_money(total_expense)}")

    print("  " + "—" * 35)

    print("\n  EXPENSES BY CATEGORY")
    print("  " + "—" * 35)

    if not expenses_by_category:
        print("  (No expense transactions logged yet)")

    else:
        for category, amount in expenses_by_category.items():
            print(
                f"  {category.title():<18} "
                f"{format_money(amount):>16}"
            )

    print("  " + "—" * 35 + "\n")