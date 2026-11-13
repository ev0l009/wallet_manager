from enum import Enum

class AccDashState(Enum):
    """Navigation states for individual account inspection dashboards."""

    ACC_DASH = "acc_dash"
    BALANCE = "balance"
    DEPOSIT = "deposit"
    WITHRAWAL = "withdrawal"
    DEACTIVATE = "deactivate"
    RETURN = "return"

class AccType(Enum):
    """Supported underlying storage classification for accounts."""

    BANK = "bank"
    CASH = "cash"
    SAVINGS = "savings"
    MOBILE = "mobile"

class AccStat(Enum):
    """Lifecycle states for operational accounts."""

    ACTIVE = "active"
    INACTIVE = "inactive"

class TrxType(Enum):
    """Financial tracking action classifications."""

    TRANSFER = "transfer"
    WITHDRAW = "withdraw"
    DEPOSIT = "deposit"