"""Custom exception hierarchy for the Finance Tracker application."""


# --- APPLICATION BASE ---
class WalletError(Exception):
    """Base exception for all application-specific errors."""
    pass


# --- VALIDATION ERRORS ---
class ValidationError(WalletError):
    """Raised when supplied data violates validation requirements."""
    pass


class InvalidAccountIdError(ValidationError):
    pass


class InvalidTransactionIdError(ValidationError):
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


# --- BUSINESS RULE ERRORS ---
class BusinessRuleError(WalletError):
    """Raised when an operation violates an application business rule."""
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


# --- ENTITY LOOKUP ERRORS ---
class EntityNotFoundError(WalletError):
    """Raised when a requested entity cannot be found."""
    pass


# --- DATA INTEGRITY ERRORS ---
class DataIntegrityError(WalletError):
    """Raised when persisted application data violates integrity rules."""
    pass


class NegativeBalanceError(DataIntegrityError):
    """Raised when historical ledger validation produces a negative balance."""
    pass


# --- PERSISTENCE ERRORS ---
class PersistenceError(WalletError):
    """Base exception for persistence operation failures."""
    pass


class StorageReadError(PersistenceError):
    pass


class StorageWriteError(PersistenceError):
    pass