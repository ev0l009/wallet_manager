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
    REVERSE_TRANSACTION = "reverse_transaction"
    REPORTS = "reports"
    REACTIVATE_ACC = "reactivate"

class AccDashState(Enum):
    """Navigation states for individual account inspection dashboards."""

    ACC_DASH = "acc_dash"
    BALANCE = "balance"
    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"
    UPDATE_ACC = "update_acc"
    ACCOUNT_TRANSACTIONS = "account_transactions"
    ACCOUNT_INFO = "account_info"
    ACCOUNT_REPORTS = "account_reports"
    DEACTIVATE = "deactivate"
    RETURN = "return"