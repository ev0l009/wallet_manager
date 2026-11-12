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