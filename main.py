"""Main entry point for the Finance Tracker application.
 
This module manages the application lifecycle, menu state transitions, and user interface routing through a simplified state-based architecture.

It initializes the wallet engine, loads persisted application data, dispatches user-selected operations, and handles application termination.

Unexpected runtime exceptions are captured at the application boundary and recorded in the application log. """

import sys

from models.wallet_engine import WalletEngine
from ui.menu_states import MenuState 
from ui.menus import (
    get_main_menu_state,
    select_acc
)
from ui.views import (
    display_active_accounts,
    display_acc_bal,
    display_transactions,
    display_reports
)

from utils.logger import configure_logger

# Initialize the application-wide logger.

logger = configure_logger()

def wallet_runner() -> None: 
    """Initialize and execute the main application loop.

    Creates the wallet engine, loads existing application data, and
    routes execution according to the current menu state.

    Each menu state delegates its corresponding operation to the
    wallet engine before returning control to the main dashboard.

    The application terminates when the EXIT state is selected.
    """

    # Initialize the wallet engine and load persisted application data.
    wallet = WalletEngine()
    # wallet.load()

    # Start the application at the main dashboard.
    current_state = MenuState.DASHBOARD.value

    # Main application loop: route execution based on the active menu state.
    while current_state != MenuState.EXIT.value:

        # Display the main dashboard and retrieve the user's selection.
        if current_state == MenuState.DASHBOARD.value:
            current_state = get_main_menu_state()

        # Account management operations.
        elif current_state == MenuState.CREATE_ACCOUNT.value:
            wallet.create_account()
            current_state = MenuState.DASHBOARD.value

        elif current_state == MenuState.LIST_ACCOUNTS.value:
            active_accounts = wallet.get_active_accounts()
            display_active_accounts(active_accounts)
            current_state = MenuState.DASHBOARD.value

        elif current_state == MenuState.ACC_DASHBOARD.value:
            acc_map = wallet.get_active_acc_map()
            selected_acc = select_acc(acc_map)
            if selected_acc:
                acc_bal = wallet.get_acc_bal(selected_acc)
                display_acc_bal(acc_bal)
            current_state = MenuState.DASHBOARD.value

        elif current_state == MenuState.REACTIVATE_ACC.value:
            acc_map = wallet.get_inactive_acc_map()
            selected_acc = select_acc(acc_map)
            if selected_acc:
                wallet.reactivate_acc(selected_acc)
            current_state = MenuState.DASHBOARD.value

        # Financial transaction operations.
        elif current_state == MenuState.TRANSFER.value:
            acc_map = wallet.get_active_acc_map()
            source_acc_id = select_acc(acc_map)
            raw_amt = input("Enter amount: ").strip()
            target_acc_id = select_acc(acc_map=acc_map, id_to_skip=source_acc_id)
            raw_date = input("Enter transaction date [YYYY-MM-DD]: ").strip()
            if (
                source_acc_id and 
                target_acc_id and 
                raw_amt and 
                raw_date
            ):
                wallet.record_transfer(
                    source_acc_id=source_acc_id,
                    target_acc_id=target_acc_id,
                    inp_amt=raw_amt,
                    inp_date=raw_date
                )
            current_state = MenuState.DASHBOARD.value

        elif current_state == MenuState.TRANSACTIONS.value:
            transactions = wallet.get_transactions()
            if transactions:
                display_transactions(transactions)
            current_state = MenuState.DASHBOARD.value

        # Financial reporting operations.
        elif current_state == MenuState.REPORTS.value:
            transactions = wallet.get_transactions()
            if transactions:
                display_reports(transactions)
            current_state = MenuState.DASHBOARD.value

        # Prevent unsupported states from causing an infinite loop.
        else:
            logger.warning(
                "Unrecognized menu state encountered: %s",
                current_state
            )
            current_state = MenuState.DASHBOARD.value

    print("\n  • Exiting Finance Tracker...")


try:
    # Start the application.
    wallet_runner()

except Exception:
    # Log unexpected exceptions with their complete traceback.
    logger.exception("Unexpected application failure.")

    # Display a generic error message without exposing internal details.
    print(
        "\n[CRITICAL ERROR] An unexpected system error occurred."
    )
    print(
        "The application encountered a problem and must close."
    )
    print(
        "Error details have been recorded in the application log."
    )

    # Terminate with a non-zero exit status.
    sys.exit(1)