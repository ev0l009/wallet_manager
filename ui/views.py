from __future__ import annotations
from typing import TYPE_CHECKING

from models.enums import TrxType

if TYPE_CHECKING:
     from models.account import Account
     from models.transaction import Transaction

def display_active_accounts(active_accounts: list[ Account ]) -> None:
        """Renders a formatted text grid table displaying active accounts in memory."""
        print("\n  ACTIVE ACCOUNTS")
        print("  " + "—" * 58)
        
        if not active_accounts:
            print("  [i] There are no active accounts right now.\n")
            return

        print(f"  {'Account Name':<16} {'Account ID':<12} {'Type':<12} {'Balance':>12}")
        print("  " + "—" * 58)
        
        for acc in active_accounts:
            # Prevent grid breakage by truncating names longer than 14 characters
            if len(acc.acc_name) > 14:
                name_trunc = f"{acc.acc_name.title()[:14]}.."
            else:
                name_trunc = acc.acc_name.title()
                
            type_str = acc.acc_type.capitalize()
            balance_str = f"${acc.balance:,.2f}"
            
            print(f"  {name_trunc:<16} {acc.id:<12} {type_str:<12} {balance_str:>12}")
            
        print("  " + "—" * 58 + "\n")


def display_acc_bal(acc_bal: int):
    print("\n  CURRENT BALANCE")
    print("  " + "—" * 25)
    print(f"  Available Funds:  ${acc_bal:,.2f}")
    print("  " + "—" * 25 + "\n")


def display_transactions(transactions: list[ Transaction ]) -> None:
        """Renders a structured grid report of historical transaction records."""
        if not transactions:
            print("\n  [!] No transactions found in this ledger.\n")
            return

        print("\n  TRANSACTION HISTORY")
        print("  " + "—" * 45)
        print(f"  {'ID':<13} {'Type':<11} {'Amount':>16}")
        print("  " + "—" * 45)

        for trx in transactions:
            trx_id = trx.id
            trx_type = trx.transaction_type.capitalize()
            
            # Explicit directional labeling based on specific financial context types
            if trx.transaction_type == TrxType.DEPOSIT.value:
                amt_str = f"+${trx.amount:,.2f}"
            elif trx.transaction_type == TrxType.TRANSFER.value:
                amt_str = f"⇄ ${trx.amount:,.2f}"
            else:
                amt_str = f"-${trx.amount:,.2f}"

            print(f"  {trx_id:<13} {trx_type:<11} {amt_str:>16}")

        print("  " + "—" * 45 + "\n")


def display_reports(transactions: list[ Transaction ]) -> None:
    """Generates comprehensive aggregated summaries of global accounting metrics."""
    total_income = sum([
        t.amount for t in  transactions
        if t.transaction_type == TrxType.DEPOSIT.value
    ])

    total_expense = sum([
        t.amount for t in  transactions
        if t.transaction_type == TrxType.WITHDRAW.value
    ])

    net_balance = total_income - total_expense

    expense_category: dict[str, int] = {}
    
    for trx in transactions:
        if trx.transaction_type == TrxType.WITHDRAW.value:
            cat = trx.category.title() # type: ignore
            expense_category[cat] = expense_category.get(cat, 0) + trx.amount # type: ignore

        print("\n  FINANCIAL REPORT OVERVIEW")
        print("  " + "—" * 35)
        print(f"  Net Total Balance:  ${net_balance:,.2f}")
        print(f"  Total Income (+):   ${total_income:,.2f}")
        print(f"  Total Expenses (-): ${total_expense:,.2f}")
        print("  " + "—" * 35)

        print("\n  EXPENSES BY CATEGORY")
        print("  " + "—" * 35)
        
        if not expense_category:
            print("  (No expense transactions logged yet)")
        else:
            for cat, amt in expense_category.items():
                print(f"  {cat:<18} ${amt:>12,.2f}")
                
        print("  " + "—" * 35 + "\n")