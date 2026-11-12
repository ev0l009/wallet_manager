from exceptions.errors import (
    InvalidAccountNameError,
    DuplicateAccountNameError
)

def get_valid_acc_name(existing_names: dict[str, str]) -> str:
    """Collect and validate a new account name.

    Args:
        existing_names: Mapping of account IDs to existing account names.

    Returns:
        str: Normalized and validated account name.

    Raises:
        InvalidAccountNameError: If the name violates naming constraints.
        DuplicateAccountNameError: If the name already exists.
    """

    raw_name = input("  Enter account name → ")
    cleaned_name = raw_name.strip()

    if not cleaned_name:
        raise InvalidAccountNameError(
            "Account name cannot be empty."
        )

    if not 4 <= len(cleaned_name) <= 20:
        raise InvalidAccountNameError(
            "Account name must contain between 4 and 20 characters."
        )

    normalized_name = cleaned_name.casefold()

    existing_normalized_names = {
        name.strip().casefold()
        for name in existing_names.values()
    }

    if normalized_name in existing_normalized_names:
        raise DuplicateAccountNameError(
            "An account with this name already exists."
        )

    return cleaned_name
