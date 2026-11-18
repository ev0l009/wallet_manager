from __future__ import annotations

from typing import TYPE_CHECKING

from models.enums import TrxType
from models.types import FundedAccDict

if TYPE_CHECKING:
    from models.transaction import Transaction


def format_money(amount_kobo: int) -> str:
    """Formats an integer Kobo amount as Nigerian Naira.

    Args:
        amount_kobo: Monetary amount represented in Kobo.

    Returns:
        str: Formatted Naira amount without floating-point conversion.
    """
    sign = "-" if amount_kobo < 0 else ""
    naira, kobo = divmod(abs(amount_kobo), 100)

    return f"{sign}₦{naira:,}.{kobo:02d}"


def display_active_accounts(
    funded_active_accounts: list[FundedAccDict]
) -> None:
    """Displays a formatted table of active accounts.

    Args:
        funded_active_accounts: Accounts eligible for display.
    """
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
        type_str = acc["acc_type"].capitalize()
        balance_str = format_money(acc["acc_bal"])

        print(
            f"  {name:<20} "
            f"{acc_id:<36} "
            f"{type_str:<12} "
            f"{balance_str:>16}"
        )

    print("  " + "—" * 90 + "\n")


def display_acc_bal(acc_bal: int) -> None:
    """Displays the available balance of an account.

    Args:
        acc_bal: Account balance represented in Kobo.
    """
    print("\n  CURRENT BALANCE")
    print("  " + "—" * 25)
    print(f"  Available Funds:  {format_money(acc_bal)}")
    print("  " + "—" * 25 + "\n")


def display_transactions(
    transactions: list[Transaction]
) -> None:
    """Displays historical transaction records.

    Preserves visibility of original transactions and their reversals.
    """
    if not transactions:
        print("\n  [!] No transactions found in this ledger.\n")
        return

    print("\n  TRANSACTION HISTORY")
    print("  " + "—" * 70)
    print(
        f"  {'ID':<15} "
        f"{'Type':<11} "
        f"{'Amount':>18}"
        f"{'Date':>18}"
    )
    print("  " + "—" * 70)

    for trx in transactions:
        trx_id = trx.id
        trx_type = trx.transaction_type.capitalize()
        amount = format_money(abs(trx.amount))

        if trx.transaction_type == TrxType.DEPOSIT.value:
            amt_str = f"+{amount}"

        elif trx.transaction_type == TrxType.WITHDRAW.value:
            amt_str = f"-{amount}"

        elif trx.transaction_type == TrxType.TRANSFER.value:
            amt_str = f"⇄ {amount}"

        elif trx.transaction_type == TrxType.REVERSAL.value:
            amt_str = f"↶ {amount}"

        else:
            amt_str = f"? {format_money(trx.amount)}"

        if hasattr(trx.transaction_date, "strftime"):
            date_str = trx.transaction_date.strftime("%Y-%m-%d")
        else:
            date_str = str(trx.transaction_date or "N/A")

        print(
            f"  {trx_id:<15} "
            f"{trx_type:<11} "
            f"{amt_str:>18}"
            f"{date_str:>18}"
        )

    print("  " + "—" * 70 + "\n")


def display_reports(
    total_income: int,
    total_expense: int,
    net_delta: int,
    expenses_by_category: dict[str, int],
) -> None:
    """Displays pre-calculated financial reporting figures.

    All monetary values must be supplied in Kobo.

    Args:
        total_income: Total income for the reporting period.
        total_expense: Total expenses for the reporting period.
        net_delta: Net income minus expenses for the reporting period.
        expenses_by_category: Pre-calculated expense totals grouped
            by category.
    """
    print("\n  FINANCIAL REPORT OVERVIEW")
    print("  " + "—" * 35)

    print(f"  Net Delta:          {format_money(net_delta)}")
    print(f"  Total Income (+):   {format_money(total_income)}")
    print(f"  Total Expenses (-): {format_money(total_expense)}")

    print("  " + "—" * 35)

    print("\n  EXPENSES BY CATEGORY")
    print("  " + "—" * 35)

    if not expenses_by_category:
        print("  (No expense transactions logged yet)")

    else:
        for cat, amount in expenses_by_category.items():
            print(
                f"  {cat.title():<18} "
                f"{format_money(amount):>16}"
            )

    print("  " + "—" * 35 + "\n")