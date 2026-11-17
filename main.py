"""Main entry point for the Finance Tracker application.
 
This module manages the application lifecycle, menu state transitions, and user interface routing through a simplified state-based architecture.

It initializes the wallet engine, loads persisted application data, dispatches user-selected operations, and handles application termination.

Unexpected runtime exceptions are captured at the application boundary and recorded in the application log. """

import sys

from services.wallet_engine import WalletEngine
from ui.menu_states import MenuState 
from ui.menus import (
    get_main_menu_state,
    select_acc,
)
from ui.views import display_transactions

from handlers import (
    create_account,
    record_transfer,
    record_reversal,
    show_active_accounts,
    manage_account,
    show_reports
)

from ui.menu_states import AccDashState

from exceptions.errors import WalletError

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
    wallet.load()

    # Start the application at the main dashboard.
    current_state = MenuState.DASHBOARD

    # Main application loop: route execution based on the active menu state.
    while True:

        # Display the main dashboard and retrieve the user's selection.
        if current_state == MenuState.DASHBOARD:
            current_state = get_main_menu_state()

        # Account management operations.
        elif current_state == MenuState.CREATE_ACCOUNT:

            acc_map = wallet.get_active_acc_map()
            create_account( wallet, acc_map )

            current_state = MenuState.DASHBOARD

        elif current_state == MenuState.LIST_ACCOUNTS:

            show_active_accounts(wallet)
            current_state = MenuState.DASHBOARD

        # Financial transaction operations.
        elif current_state == MenuState.TRANSFER:
            acc_map = wallet.get_active_acc_map()

            record_transfer( wallet, acc_map )

            current_state = MenuState.DASHBOARD

        elif current_state == MenuState.ACC_DASHBOARD:
            manage_account( wallet )    

            current_state = MenuState.DASHBOARD

        elif current_state == MenuState.TRANSACTIONS:
            transactions = wallet.get_transactions()
            display_transactions(transactions)
            current_state = MenuState.DASHBOARD

        elif current_state == MenuState.REVERSE_TRANSACTION:
            record_reversal( wallet )
            
            current_state = MenuState.DASHBOARD

        elif current_state == MenuState.REACTIVATE_ACC:
            acc_map = wallet.get_inactive_acc_map()
            selected_acc = select_acc(acc_map)

            if selected_acc:
                wallet.reactivate_acc(selected_acc)

            current_state = MenuState.DASHBOARD

        # Financial reporting operations.
        elif current_state == MenuState.REPORTS:
            show_reports(wallet)
            current_state = MenuState.DASHBOARD

        elif current_state == MenuState.EXIT:
            print("\n  • Exiting Finance Tracker...")
            break

        # Prevent unsupported states from causing an infinite loop.
        else:
            logger.warning(
                "Unrecognized menu state encountered: %s",
                current_state
            )
            current_state = MenuState.DASHBOARD



if __name__ == "__main__":
    try:
        wallet_runner()
    except Exception:
        logger.exception("Unexpected application failure.")
        print("\n[CRITICAL ERROR] An unexpected system error occurred.")
        print("The application encountered a problem and must close.")
        print("Error details have been recorded in the application log.")
        sys.exit(1)