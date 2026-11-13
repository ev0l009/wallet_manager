from ui.menu_states import MenuState
from models.enums import (
    AccType,
    AccDashState
)
from exceptions.errors import InvalidAccountTypeError

def get_main_menu_state() -> str:
    """Displays the main menu interface and captures the next navigation state.

    Returns:
        str: The string value mapping to the next target MenuState.
    """
    options = {
        "1": MenuState.CREATE_ACCOUNT.value,
        "2": MenuState.LIST_ACCOUNTS.value,
        "3": MenuState.TRANSFER.value,
        "4": MenuState.ACC_DASHBOARD.value,
        "5": MenuState.TRANSACTIONS.value,
        "6": MenuState.REACTIVATE_ACC.value,
        "7": MenuState.REPORTS.value,
        "8": MenuState.EXIT.value,
    }

    print("\n  FINANCE TRACKER")
    print("  " + "—" * 20)
    print("  1. Create Account")
    print("  2. List Accounts")
    print("  3. Transfer Funds")
    print("  4. Inspect Account")
    print("  5. Transactions")
    print("  6. Reactivate Account")
    print("  7. Reports")
    print("  8. Exit\n")

    choice = input("  Select option (1-8) → ").strip()

    if choice not in options:
        print("\n  [!] Invalid choice. Please try again.")
        return MenuState.DASHBOARD.value

    return options[choice]


def get_acc_type() -> str:
    """Prompt the user to select an account classification.

    Returns:
        str: The selected account type.

    Raises:
        InvalidAccountTypeError: If the selection is invalid.
    """

    options = {
        "1": AccType.BANK.value,
        "2": AccType.CASH.value,
        "3": AccType.SAVINGS.value,
        "4": AccType.MOBILE.value,
    }

    print("\n  SELECT ACCOUNT TYPE")
    print("  " + "—" * 24)
    print("  1. Bank")
    print("  2. Cash")
    print("  3. Savings")
    print("  4. Mobile Wallet\n")

    choice = input("  Select option (1-4) → ").strip()

    if choice not in options:
        raise InvalidAccountTypeError(
            "Invalid selection. Choose an option between 1 and 4."
        )

    return options[choice]


def get_acc_dash_state(acc_name: str) -> str:
    """Displays the individual account inspection actions sub-menu.

    Args:
        acc_name: The descriptive string name of the account under inspection.

    Returns:
        str: The string value mapping to the next target AccDashState.
    """
    options = {
        "1": AccDashState.BALANCE.value,
        "2": AccDashState.DEPOSIT.value,
        "3": AccDashState.WITHRAWAL.value,
        "4": AccDashState.DEACTIVATE.value,
        "5": AccDashState.RETURN.value,
    }

    print(f"\n  ACCOUNT: {acc_name.upper()}")
    print("  " + "—" * 20)
    print("  1. Check Balance")
    print("  2. Deposit")
    print("  3. Withdraw")
    print("  4. Deactivate Account")
    print("  5. Main Menu\n")

    choice = input("  Select option (1-5) → ").strip()

    if choice not in options:
        print("\n  [!] Invalid choice. Please try again.")
        return AccDashState.ACC_DASH.value

    return options[choice]