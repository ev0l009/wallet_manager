from enum import Enum

class AccType(Enum):
    """Supported account classifications."""

    BANK = "bank"
    CASH = "cash"
    SAVINGS = "savings"
    MOBILE_WALLET = "mobile_wallet"


class AccStat(Enum):
    """Lifecycle states for operational accounts."""

    ACTIVE = "active"
    INACTIVE = "inactive"


class TrxType(Enum):
    """Supported financial transaction classifications."""

    INCOME = "income"
    EXPENSE = "expense"
    TRANSFER = "transfer"


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
