"""Presentation menus for application navigation and user selection."""

from ui.menu_states import MenuState, AccDashState

from models.enums import (
    AccType,
    ExpCatOpts,
)


def get_main_menu_state() -> MenuState:
    """Display the main menu and capture the next navigation state."""

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
    """Prompt the user to select an account classification."""

    options = {
        "1": AccType.BANK.value,
        "2": AccType.CASH.value,
        "3": AccType.SAVINGS.value,
        "4": AccType.MOBILE_WALLET.value,
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
    """Display the individual account inspection menu."""

    options = {
        "1": AccDashState.BALANCE,
        "2": AccDashState.DEPOSIT,
        "3": AccDashState.WITHDRAWAL,
        "4": AccDashState.UPDATE_ACC,
        "5": AccDashState.ACCOUNT_TRANSACTIONS,
        "6": AccDashState.ACCOUNT_INFO,
        "7": AccDashState.ACCOUNT_REPORTS,
        "8": AccDashState.DEACTIVATE,
        "9": AccDashState.RETURN,
    }

    print(f"\n  ACCOUNT: {acc_name.upper()}")
    print("  " + "—" * 20)
    print("  1. Check Balance")
    print("  2. Deposit")
    print("  3. Withdraw")
    print("  4. Update Account Name")
    print("  5. View Transactions")
    print("  6. Account Information")
    print("  7. Account Reports")
    print("  8. Deactivate Account")
    print("  9. Main Menu\n")

    choice = input("  Select option (1-9) → ").strip()

    if choice not in options:
        print("\n  [!] Invalid choice. Please try again.")
        return AccDashState.ACC_DASH

    return options[choice]


def select_acc(
    acc_map: dict[str, str],
    id_to_skip: str | None = None,
    heading: str | None = None,
) -> str | None:
    """Display accounts and capture the user's selection."""

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
    """Present expense categories and capture the user's selection."""

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

    print("\n  SELECT EXPENSE CATEGORY")
    print("  " + "—" * 25)

    for idx, category in cat_options.items():
        print(f"  {idx}. {category.capitalize()}")

    print()

    choice = input(
        f"  Select option (1-{len(cat_options)}) → "
    ).strip()

    if choice not in cat_options:
        print("\n  Invalid category selection. Selection canceled.")
        return None

    return cat_options[choice]