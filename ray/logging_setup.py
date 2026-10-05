import logging
from logging.handlers import RotatingFileHandler

from ray.config import LOGS_DIR

LOG_FORMAT = "%(asctime)s | %(levelname)-7s | %(name)s | %(message)s"
MAX_LOG_BYTES = 1_000_000
BACKUP_COUNT = 3


def setup_logging(level: str = "INFO") -> None:
    root_logger = logging.getLogger()
    if root_logger.handlers:
        return

    LOGS_DIR.mkdir(exist_ok=True)
    formatter = logging.Formatter(LOG_FORMAT)

    file_handler = RotatingFileHandler(
        LOGS_DIR / "ray.log",
        maxBytes=MAX_LOG_BYTES,
        backupCount=BACKUP_COUNT,
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    root_logger.setLevel(level)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
