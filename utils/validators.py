from exceptions.errors import (
    InvalidAccountNameError,
    DuplicateAccountNameError,
    InvalidDateError,
    InvalidAmountError
)

from datetime import datetime, date

import re
from decimal import Decimal, InvalidOperation

def convert_to_kobo(user_input: str) -> int:
    if not isinstance(user_input, str):
        raise InvalidAmountError()

    value = user_input.strip()

    if not re.fullmatch(r"\d+(?:\.\d{1,2})?", value):
        raise InvalidAmountError()

    try:
        amount = Decimal(value)

        if not amount.is_finite() or amount <= 0:
            raise InvalidAmountError()

        if amount > Decimal("99999999.99"):
            raise InvalidAmountError()

        return int(amount * 100)

    except InvalidOperation:
        raise InvalidAmountError()
    

def get_valid_acc_name(raw_name: str, existing_names: dict[str, str]) -> str:
    """Collect and validate a new account name.

    Args:
        existing_names: Mapping of account IDs to existing account names.

    Returns:
        str: Normalized and validated account name.

    Raises:
        InvalidAccountNameError: If the name violates naming constraints.
        DuplicateAccountNameError: If the name already exists.
    """

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

def get_valid_date(raw_date: str) -> date:
    if not isinstance(raw_date, str):
        raise InvalidDateError("Date must be a string.")

    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", raw_date):
        raise InvalidDateError(
            f"'{raw_date}' must follow YYYY-MM-DD format."
        )

    try:
        parsed_date = datetime.strptime(
            raw_date, "%Y-%m-%d"
        ).date()

    except ValueError as err:
        raise InvalidDateError(
            f"'{raw_date}' is not a valid calendar date."
        ) from err

    if parsed_date > date.today():
        raise InvalidDateError(
            f"'{raw_date}' cannot be in the future."
        )

    return parsed_date