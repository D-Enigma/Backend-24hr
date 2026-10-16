import logging
from logging.handlers import RotatingFileHandler


# Use one logger throughout the application to keep track of important events.
logger = logging.getLogger("backend")
logger.setLevel(logging.INFO)

# Avoid adding duplicate handlers if this module is imported multiple times.
if not logger.handlers:
    # Write logs to app.log and rotate the file when it reaches roughly 1 MB.
    # Keep the three previous log files so older errors aren't lost immediately.
    handler = RotatingFileHandler(
        "app.log", maxBytes=1_000_000, backupCount=3, encoding="utf-8"
    )

    # Include the time, log level, and message in every log entry.
    formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")

    handler.setFormatter(formatter)
    logger.addHandler(handler)
