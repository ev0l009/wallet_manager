from enum import Enum

class MenuState(Enum):
    """Application-level navigation states for the primary loop."""

    DASHBOARD = "dashboard"
    EXIT = "exit"
    CREATE_ACCOUNT = "create_account"
    LIST_ACCOUNTS = "list_accounts"
    TRANSFER = "transfer"
    ACC_DASHBOARD = "acc_dashboard"
    TRANSACTIONS = "transactions"
    REPORTS = "reports"
    REACTIVATE_ACC = "reactivate"

class AccDashState(Enum):
    """Navigation states for individual account inspection dashboards."""

    ACC_DASH = "acc_dash"
    BALANCE = "balance"
    DEPOSIT = "deposit"
    WITHRAWAL = "withdrawal"
    DEACTIVATE = "deactivate"
    RETURN = "return"