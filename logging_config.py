import logging
from logging.handlers import RotatingFileHandler

logger = logging.getLogger("backend")
logger.setLevel(logging.INFO)

if not logger.handlers:
    handler = RotatingFileHandler(
        "app.log", maxBytes=1_000_000, backupCount=3, encoding="utf-8"
    )

    formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")

    handler.setFormatter(formatter)
    logger.addHandler(handler)
