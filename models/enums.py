from enum import Enum

class AccType(Enum):
    """Supported account classifications."""

    BANK = "bank"
    CASH = "cash"
    SAVINGS = "savings"
    MOBILE = "mobile"


class AccStat(Enum):
    """Lifecycle states for operational accounts."""

    ACTIVE = "active"
    INACTIVE = "inactive"


class TrxType(Enum):
    """Financial transaction classifications."""

    TRANSFER = "transfer"
    WITHDRAW = "withdraw"
    DEPOSIT = "deposit"
    REVERSAL = "reversal"


class ExpCatOpts(Enum):
    """Valid expense categories."""

    FOOD = "food"
    BILLS = "bills"
    TRANSPORT = "transport"
    AIRTIME = "airtime"
    HEALTH = "health"
    SHOPPING = "shopping"
    ENTERTAINMENT = "entertainment"
    OTHERS = "others"
