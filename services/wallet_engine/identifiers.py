"""Identifier generation utilities for the wallet engine."""

import secrets
import string

from typing import Final

from models.types import WalletEngineData
from exceptions.errors import InvalidAccountIdError


ACC_ID_PREFIX: Final[str] = "acc"
TRX_ID_PREFIX: Final[str] = "trx"


def generate_id(prefix: str, data: WalletEngineData) -> str:
    """Generate a unique identifier for an account or transaction."""

    if prefix not in {ACC_ID_PREFIX, TRX_ID_PREFIX}:
        raise InvalidAccountIdError(
            f"Unsupported identifier prefix: {prefix}"
        )

    pool = string.ascii_letters + string.digits

    while True:
        suffix = "".join(secrets.choice(pool) for _ in range(5))
        generated_id = f"{prefix}_{suffix}"

        if prefix == ACC_ID_PREFIX:
            if generated_id not in data["accounts"]:
                return generated_id

        elif not any(
            transaction.id == generated_id
            for transaction in data["transactions"]
        ):
            return generated_id