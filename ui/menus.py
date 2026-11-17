from ui.menu_states import MenuState, AccDashState
from models.enums import (
    AccType,
    ExpCatOpts
)


def get_main_menu_state() -> MenuState:
    """Displays the main menu and captures the next navigation state.

    Returns:
        MenuState: The selected navigation state.
            Returns MenuState.DASHBOARD if the selection is invalid.
    """
    options = {
        "1": MenuState.CREATE_ACCOUNT,
        "2": MenuState.LIST_ACCOUNTS,
        "3": MenuState.TRANSFER,
        "4": MenuState.ACC_DASHBOARD,
        "5": MenuState.TRANSACTIONS,
        "6": MenuState.REACTIVATE_ACC,
        "7": MenuState.REPORTS,
        "8": MenuState.EXIT,
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
        return MenuState.DASHBOARD

    return options[choice]


def get_acc_type() -> str | None:
    """Prompts the user to select an account classification.

    Returns:
        str: The selected account type.
        None: If the selection is invalid.
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
        print("\n  [!] Invalid account type selection.")
        return None

    return options[choice]


def get_acc_dash_state(acc_name: str) -> AccDashState:
    """Displays the individual account inspection actions sub-menu.

    Args:
        acc_name: The descriptive name of the account under inspection.

    Returns:
        AccDashState: The selected account dashboard navigation state.
            Returns AccDashState.ACC_DASH if the selection is invalid.
    """
    options = {
        "1": AccDashState.BALANCE,
        "2": AccDashState.DEPOSIT,
        "3": AccDashState.WITHDRAWAL,
        "4": AccDashState.DEACTIVATE,
        "5": AccDashState.RETURN,
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
        return AccDashState.ACC_DASH

    return options[choice]


def select_acc(
    acc_map: dict[str, str],
    id_to_skip: str | None = None,
    heading: str | None = None,
) -> str | None:
    """Displays a dynamically numbered list of accounts for selection.

    Args:
        acc_map: Mapping of account IDs to account names.
        id_to_skip: Optional account ID to exclude from selection.
        heading: Optional custom heading for the selection menu.

    Returns:
        str: The selected account ID.
        None: If no eligible accounts exist or the selection is invalid.
    """
    options: dict[str, str] = {}
    title_text = heading.upper() if heading else "SELECT ACCOUNT"

    print(f"\n  {title_text}")
    print("  " + "—" * 25)

    idx = 1

    for acc_id, acc_name in acc_map.items():
        if acc_id == id_to_skip:
            continue

        print(f"  {idx}. {acc_name.title()}")
        options[str(idx)] = acc_id
        idx += 1

    if not options:
        print("\n  No eligible accounts available.")
        return None

    print()
    choice = input(
        f"  Select option (1-{len(options)}) → "
    ).strip()

    if choice not in options:
        print("\n  Invalid account selection. Selection canceled.")
        return None

    return options[choice]


def get_exp_category() -> str | None:
    """Presents recognized expense categorization options.

    Returns:
        str: The selected expense category.
        None: If the selection is invalid.
    """
    cat_options = {
        "1": ExpCatOpts.FOOD.value,
        "2": ExpCatOpts.BILLS.value,
        "3": ExpCatOpts.TRANSPORT.value,
        "4": ExpCatOpts.AIRTIME.value,
        "5": ExpCatOpts.HEALTH.value,
        "6": ExpCatOpts.SHOPPING.value,
        "7": ExpCatOpts.ENTERTAINMENT.value,
        "8": ExpCatOpts.OTHERS.value,
    }

    print("\n  Select category:")

    for idx, cat in cat_options.items():
        print(f"  {idx}. {cat.capitalize()}")

    print()
    choice = input(
        f"  Select option (1-{len(cat_options)}) → "
    ).strip()

    if choice not in cat_options:
        print("\n  Invalid category selection. Selection canceled.")
        return None

    return cat_options[choice]