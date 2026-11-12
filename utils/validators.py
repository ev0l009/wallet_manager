
def get_valid_acc_name(existing_names: dict[str, str]) -> str:
    """Validates an account name against length constraints and duplicates.

    Args:
        value: The raw string input provided by the user.
        existing_names: A mapping containing current system account names.

    Returns:
        str: The safely stripped, validated account name string.

    Raises:
        AccNameError: If the name is blank, under 3 characters, or a duplicate.
    """
    raw_name = input("  Enter account name → ").strip()
    cleaned_name = raw_name.strip()

    if not cleaned_name:
        raise ValueError("Account name cannot be empty.")

    if len(cleaned_name) < 3:
        raise ValueError("Account name cannot be less than 3 characters.")

    if cleaned_name in existing_names.values():
        raise ValueError("An account with this name already exists.")

    return cleaned_name