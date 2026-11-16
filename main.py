"""Main entry point for the Finance Tracker application.
 
This module manages the application lifecycle, menu state transitions, and user interface routing through a simplified state-based architecture.

It initializes the wallet engine, loads persisted application data, dispatches user-selected operations, and handles application termination.

Unexpected runtime exceptions are captured at the application boundary and recorded in the application log. """

import sys

from models.wallet_engine import WalletEngine
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
    acc_map = wallet.get_active_acc_map()

    # Start the application at the main dashboard.
    current_state = MenuState.DASHBOARD.value

    # Main application loop: route execution based on the active menu state.
    while current_state != MenuState.EXIT.value:

        # Display the main dashboard and retrieve the user's selection.
        if current_state == MenuState.DASHBOARD.value:
            current_state = get_main_menu_state()

        # Account management operations.
        elif current_state == MenuState.CREATE_ACCOUNT.value:
            raw_name = input("  Enter account name → ")
            try:
                acc_name = get_valid_acc_name(raw_name, acc_map)
                acc_type = get_acc_type()
                wallet.create_account(acc_name,acc_type)
            except WalletError as err:
                print(err)
            else:
                print("\n  [✓] Account created successfully.")
            current_state = MenuState.DASHBOARD.value

        elif current_state == MenuState.LIST_ACCOUNTS.value:

            active_accounts = wallet.get_active_accounts()
            funded_active_accounts = [
                {
                    **acc.to_dict(), 
                    "acc_bal": wallet.get_acc_bal(acc.id)
                }
                for acc in active_accounts
            ]
            
            display_active_accounts(funded_active_accounts)

            current_state = MenuState.DASHBOARD.value

        # Financial transaction operations.
        elif current_state == MenuState.TRANSFER.value:
            try:
                source_acc_id = select_acc(acc_map)
                raw_amt = input("Enter amount: ").strip()
                target_acc_id = select_acc(
                    acc_map=acc_map, 
                    id_to_skip=source_acc_id
                )
                raw_date = input("Enter transaction date [YYYY-MM-DD]: ").strip()

                wallet.record_transfer(
                    source_acc_id=source_acc_id,
                    target_acc_id=target_acc_id,
                    inp_amt=raw_amt,
                    inp_date=raw_date
                )
            except WalletError as err:
                print(err)
            else:
                print("\n  [✓] Transfer record successful.")
            current_state = MenuState.DASHBOARD.value

        elif current_state == MenuState.ACC_DASHBOARD.value:
            
            selected_acc_id = select_acc(acc_map)

            if selected_acc_id:

                acc = wallet.get_account(selected_acc_id)
                acc_dash_state = AccDashState.ACC_DASH.value

                while True:
                    if acc_dash_state == AccDashState.ACC_DASH.value:
                        acc_dash_state = get_acc_dash_state(acc.acc_name)

                    elif acc_dash_state == AccDashState.BALANCE.value:

                        acc_bal = wallet.get_acc_bal(acc.id)
                        display_acc_bal(acc_bal)
                        acc_dash_state = AccDashState.ACC_DASH.value

                    elif acc_dash_state == AccDashState.DEPOSIT.value:
                        
                        try:
                            raw_amt = input("Enter amount: ").strip()
                            raw_date = input("Enter transaction date [YYYY-MM-DD]: ").strip()
                            desc = input("Enter a short description: ").strip()
                            wallet.record_income(
                                acc_id=acc.id,
                                amount=raw_amt,
                                desc=desc,
                                inp_date=raw_date
                            )
                        except WalletError as err:
                            print(err)
                        else:
                            print("\n  [✓] Income record successful.")
                        acc_dash_state = AccDashState.ACC_DASH.value

                    elif acc_dash_state == AccDashState.WITHRAWAL.value:
                        raw_amt = input("Enter amount: ").strip()
                        exp_cat = get_exp_category()
                        desc = input("Enter a short description: ").strip()
                        raw_date = input("Enter transaction date [YYYY-MM-DD]: ").strip()
                        try:
                            wallet.record_expense(
                                acc_id=acc.id,
                                amount=raw_amt,
                                exp_cat=exp_cat,
                                desc=desc,
                                inp_date=raw_date
                            )
                        except WalletError as err:
                            print(err)
                        acc_dash_state = AccDashState.ACC_DASH.value

                    elif acc_dash_state == AccDashState.DEACTIVATE.value:
                        
                        acc_id = select_acc(acc_map)
                        try:
                            wallet.deactivate_acc(acc_id)
                        except WalletError as err:
                            print(err)
                        acc_dash_state = AccDashState.RETURN.value
                    elif acc_dash_state == AccDashState.RETURN.value:
                        break
                    else:
                        print("Invalid selection. try again...")
                        acc_dash_state = AccDashState.ACC_DASH.value
                            

            current_state = MenuState.DASHBOARD.value

        elif current_state == MenuState.TRANSACTIONS.value:
            transactions = wallet.get_transactions()
            if transactions:
                display_transactions(transactions)
            current_state = MenuState.DASHBOARD.value

        elif current_state == MenuState.REACTIVATE_ACC.value:
            acc_map = wallet.get_inactive_acc_map()
            selected_acc = select_acc(acc_map)
            if selected_acc:
                wallet.reactivate_acc(selected_acc)
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