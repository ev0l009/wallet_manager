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
    display_acc_bal
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
            wallet.transfer()
            current_state = MenuState.DASHBOARD.value

        elif current_state == MenuState.TRANSACTIONS.value:
            wallet.list_transactions()
            current_state = MenuState.DASHBOARD.value

        # Financial reporting operations.
        elif current_state == MenuState.REPORTS.value:
            wallet.reports()
            current_state = MenuState.DASHBOARD.value

        # Prevent unsupported states from causing an infinite loop.
        else:
            logger.warning(
                "Unrecognized menu state encountered: %s",
                current_state
            )
            current_state = MenuState.DASHBOARD.value

    # # Perform final application cleanup before termination.
    # 2. Reconsider wallet.save().

    #     Because your design uses atomic persistence after each successful operation, wallet.save() should not be necessary to commit financial transactions on exit.

    #     If it merely performs final cleanup, that's fine. Otherwise, remove it to avoid unnecessary writes or accidentally persisting uncommitted state.
    # wallet.save()

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