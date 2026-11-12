from enum import Enum

class AccType(Enum):
    """Supported underlying storage classification for accounts."""

    BANK = "bank"
    CASH = "cash"
    SAVINGS = "savings"
    MOBILE = "mobile"
