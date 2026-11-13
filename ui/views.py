from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
     from models.account import Account

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