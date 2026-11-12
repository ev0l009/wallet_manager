import logging
from pathlib import Path


def configure_logger():

    log_directory = Path("logs")
    log_directory.mkdir(exist_ok=True)

    log_file = log_directory / "wallet_manager.log"

    logging.basicConfig(
        filename=log_file,
        level=logging.ERROR,
        format=(
            "%(asctime)s | "
            "%(levelname)s | "
            "%(name)s | "
            "%(message)s"
        ),
        datefmt="%Y-%m-%d %H:%M:%S",
        encoding="utf-8"
    )

    return logging.getLogger("wallet_manager")
