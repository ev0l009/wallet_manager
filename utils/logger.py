"""Application logging configuration."""

import logging

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
LOG_DIRECTORY = PROJECT_ROOT / "logs"
LOG_FILE = LOG_DIRECTORY / "wallet_manager.log"


def configure_logger() -> logging.Logger:
    """Configure and return the application logger."""

    LOG_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True,
    )

    logging.basicConfig(
        filename=LOG_FILE,
        level=logging.ERROR,
        format=(
            "%(asctime)s | "
            "%(levelname)s | "
            "%(name)s | "
            "%(message)s"
        ),
        datefmt="%Y-%m-%d %H:%M:%S",
        encoding="utf-8",
    )

    return logging.getLogger("wallet_manager")