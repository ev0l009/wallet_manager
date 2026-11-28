"""Main entry point for the Finance Tracker application.

This module manages the application lifecycle, menu state transitions,
and user interface routing through a simplified state-based architecture.

It initializes the wallet engine, loads persisted application data,
dispatches user-selected operations, and handles application termination.

Unexpected runtime exceptions are captured at the application boundary
and recorded in the application log.
"""

import sys

from services.wallet_engine import WalletEngine

from exceptions.errors import WalletError

from ui.menu_states import MenuState

from ui.menus import (
    get_main_menu_state,
    select_acc,
)

from ui.views import display_transactions

from handlers import (
    create_account,
    record_transfer,
    show_active_accounts,
    manage_account,
    show_reports,
)

from utils.logger import configure_logger


logger = configure_logger()


def wallet_runner() -> None:
    """Initialize and execute the main application loop."""

    wallet = WalletEngine()
    wallet.load()

    current_state = MenuState.DASHBOARD

    while True:

        if current_state == MenuState.DASHBOARD:
            current_state = get_main_menu_state()

        # Account management operations.
        elif current_state == MenuState.CREATE_ACCOUNT:
            create_account(wallet)
            current_state = MenuState.DASHBOARD

        elif current_state == MenuState.LIST_ACCOUNTS:
            show_active_accounts(wallet)
            current_state = MenuState.DASHBOARD

        elif current_state == MenuState.ACC_DASHBOARD:
            manage_account(wallet)
            current_state = MenuState.DASHBOARD

        elif current_state == MenuState.REACTIVATE_ACC:
            acc_map = wallet.get_inactive_acc_map()
            selected_acc = select_acc(acc_map)

            if selected_acc is not None:
                try:
                    wallet.reactivate_acc(selected_acc)

                except WalletError as err:
                    print(err)

                else:
                    print("\n  [✓] Account reactivated successfully.")

            current_state = MenuState.DASHBOARD

        # Financial transaction operations.
        elif current_state == MenuState.TRANSFER:
            acc_map = wallet.get_active_acc_map()
            record_transfer(wallet, acc_map)
            current_state = MenuState.DASHBOARD

        elif current_state == MenuState.TRANSACTIONS:
            transactions = wallet.get_transactions()
            display_transactions(transactions)
            current_state = MenuState.DASHBOARD

        # Financial reporting.
        elif current_state == MenuState.REPORTS:
            show_reports(wallet)
            current_state = MenuState.DASHBOARD

        elif current_state == MenuState.EXIT:
            print("\n  • Exiting Finance Tracker...")
            break

        else:
            logger.warning(
                "Unrecognized menu state encountered: %s",
                current_state,
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