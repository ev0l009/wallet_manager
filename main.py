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
    get_acc_dash_state,
    get_exp_category,
    get_acc_type
)
from utils.validators import get_valid_acc_name
from ui.views import (
    display_active_accounts,
    display_acc_bal,
    display_transactions,
    display_reports
)

from handlers import (
    create_account,
    record_transfer, 
    record_income,
    record_expense
)

from ui.menu_states import AccDashState
from models.types import FundedAccDict

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

            active_accounts = wallet.get_active_accounts()
            funded_active_accounts: list[FundedAccDict] = [
                {
                    **acc.to_dict(), 
                    "acc_bal": wallet.get_acc_bal(acc.id)
                }
                for acc in active_accounts
            ]
            
            display_active_accounts(funded_active_accounts)

            current_state = MenuState.DASHBOARD

        # Financial transaction operations.
        elif current_state == MenuState.TRANSFER:
            acc_map = wallet.get_active_acc_map()

            record_transfer( wallet, acc_map )

            current_state = MenuState.DASHBOARD

        elif current_state == MenuState.ACC_DASHBOARD:
            acc_map = wallet.get_active_acc_map()
            
            selected_acc_id = select_acc(acc_map)

            if selected_acc_id:

                acc = wallet.get_account(selected_acc_id)
                acc_dash_state = AccDashState.ACC_DASH

                while True:
                    if acc_dash_state == AccDashState.ACC_DASH:
                        acc_dash_state = get_acc_dash_state(acc.acc_name)

                    elif acc_dash_state == AccDashState.BALANCE:

                        acc_bal = wallet.get_acc_bal(acc.id)
                        display_acc_bal(acc_bal)
                        acc_dash_state = AccDashState.ACC_DASH

                    elif acc_dash_state == AccDashState.DEPOSIT:
                        
                        record_income( wallet, acc.id)
                        acc_dash_state = AccDashState.ACC_DASH

                    elif acc_dash_state == AccDashState.WITHDRAWAL:
                        record_expense( wallet, acc.id )
                        acc_dash_state = AccDashState.ACC_DASH

                    elif acc_dash_state == AccDashState.DEACTIVATE:
                        acc_map = wallet.get_active_acc_map()
                        
                        acc_id = select_acc(acc_map)
                        if acc_id:

                            try:
                                wallet.deactivate_acc(acc_id)
                            except WalletError as err:
                                print(err)

                        acc_dash_state = AccDashState.RETURN

                    elif acc_dash_state == AccDashState.RETURN:
                        acc_dash_state = AccDashState.RETURN

                    else:
                        print("Invalid selection. try again...")
                            

            current_state = MenuState.DASHBOARD

        elif current_state == MenuState.TRANSACTIONS:
            transactions = wallet.get_transactions()
            if transactions:
                display_transactions(transactions)
            current_state = MenuState.DASHBOARD

        elif current_state == MenuState.REVERSE_TRANSACTION:
            original_trx_id = input("Enter the original transaction ID: ").strip()
            raw_date = input("Enter transaction date [YYYY-MM-DD]: ").strip()

            wallet.record_reversal(
                original_trx_id,
                raw_date
            )
            
            current_state = MenuState.DASHBOARD

        elif current_state == MenuState.REACTIVATE_ACC:
            acc_map = wallet.get_inactive_acc_map()
            selected_acc = select_acc(acc_map)

            if selected_acc:
                wallet.reactivate_acc(selected_acc)

            current_state = MenuState.DASHBOARD

        # Financial reporting operations.
        elif current_state == MenuState.REPORTS:
            (
                total_income, 
                total_expense, 
                net_delta, 
                expenses_by_category
            ) = wallet.get_reports()

            display_reports(
                total_income, 
                total_expense, 
                net_delta, 
                expenses_by_category
            )
            current_state = MenuState.DASHBOARD

        # Prevent unsupported states from causing an infinite loop.
        else:
            logger.warning(
                "Unrecognized menu state encountered: %s",
                current_state
            )
            current_state = MenuState.DASHBOARD

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