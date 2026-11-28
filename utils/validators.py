"""Input validation and monetary conversion utilities."""

import re

from datetime import date, datetime
from decimal import Decimal, InvalidOperation

from exceptions.errors import (
    InvalidAccountNameError,
    DuplicateAccountNameError,
    InvalidDateError,
    InvalidAmountError,
)


def convert_to_kobo(user_input: str) -> int:
    """Validate a monetary input and convert it to integer Kobo."""

    if not isinstance(user_input, str):
        raise InvalidAmountError(
            "Amount must be provided as a string."
        )

    value = user_input.strip()

    if not re.fullmatch(r"\d+(?:\.\d{1,2})?", value):
        raise InvalidAmountError(
            "Amount must be a positive monetary value "
            "with at most two decimal places."
        )

    try:
        amount = Decimal(value)

    except InvalidOperation as exc:
        raise InvalidAmountError(
            "Invalid monetary amount."
        ) from exc

    if not amount.is_finite() or amount <= 0:
        raise InvalidAmountError(
            "Amount must be greater than zero."
        )

    if amount > Decimal("99999999.99"):
        raise InvalidAmountError(
            "Amount cannot exceed ₦99,999,999.99."
        )

    return int(amount * 100)


def get_valid_acc_name(
    raw_name: str,
    existing_names: dict[str, str],
) -> str:
    """Validate and normalize an account name."""

    if not isinstance(raw_name, str):
        raise InvalidAccountNameError(
            "Account name must be a string."
        )

    cleaned_name = raw_name.strip()

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
    """Validate and parse a transaction date."""

    if not isinstance(raw_date, str):
        raise InvalidDateError(
            "Date must be a string."
        )

    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", raw_date):
        raise InvalidDateError(
            f"'{raw_date}' must follow YYYY-MM-DD format."
        )

    try:
        parsed_date = datetime.strptime(
            raw_date,
            "%Y-%m-%d",
        ).date()

    except ValueError as exc:
        raise InvalidDateError(
            f"'{raw_date}' is not a valid calendar date."
        ) from exc

    if parsed_date > date.today():
        raise InvalidDateError(
            f"'{raw_date}' cannot be in the future."
        )

    return parsed_date