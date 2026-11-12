class WalletError(Exception):
    pass

class ValidationError(WalletError):
    pass

class InvalidAmountError(ValidationError):
    pass

class InvalidDateError(ValidationError):
    pass

class InvalidAccountNameError(ValidationError):
    pass

class InvalidAccountTypeError(ValidationError):
    pass

class InvalidTransactionTypeError(ValidationError):
    pass

class InvalidCategoryError(ValidationError):
    pass

class BusinessRuleError(WalletError):
    pass

class DuplicateAccountNameError(BusinessRuleError):
    pass

class InsufficientFundsError(BusinessRuleError):
    pass

class InactiveAccountError(BusinessRuleError):
    pass

class SelfTransferError(BusinessRuleError):
    pass

class AccountBalanceNotZeroError(BusinessRuleError):
    pass

class TransactionCapacityExceededError(BusinessRuleError):
    pass

class EntityNotFoundError(WalletError):
    pass

class TransactionCorrectionError(WalletError):
    pass

class TransactionAlreadyReversedError(TransactionCorrectionError):
    pass

class InvalidReversalError(TransactionCorrectionError):
    pass

class PersistenceError(WalletError):
    pass

class DatabaseWriteException(PersistenceError):
    pass

class DatabaseCorruptedException(PersistenceError):
    pass