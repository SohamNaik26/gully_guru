"""
Logging configuration for the GullyGuru bot.
"""

import logging
import logging.config
import os
import sys
import traceback
from datetime import datetime


def configure_logging(verbose=False, log_dir="logs"):
    """
    Configure logging for the application.

    Args:
        verbose: If True, show more detailed logs
        log_dir: Directory to store log files
    """
    # Create logs directory if it doesn't exist
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Create a log file with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(log_dir, f"gullyguru_{timestamp}.log")

    # Define log levels
    console_level = "DEBUG" if verbose else "INFO"
    file_level = "DEBUG"

    config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "detailed": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s"
            },
            "simple": {"format": "%(levelname)s - %(message)s"},
        },
        "filters": {
            "telegram_filter": {
                "()": "src.utils.logging_config.TelegramFilter",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": console_level,
                "formatter": "simple",
                "filters": ["telegram_filter"],
                "stream": sys.stdout,
            },
            "file": {
                "class": "logging.FileHandler",
                "level": file_level,
                "formatter": "detailed",
                "filename": log_file,
                "mode": "a",
            },
            "error_file": {
                "class": "logging.FileHandler",
                "level": "ERROR",
                "formatter": "detailed",
                "filename": os.path.join(log_dir, f"errors_{timestamp}.log"),
                "mode": "a",
            },
        },
        "loggers": {
            "": {  # root logger
                "handlers": ["console", "file", "error_file"],
                "level": "DEBUG",
                "propagate": True,
            },
            "httpx": {
                "level": "WARNING",
                "propagate": True,
            },
            "telegram": {
                "level": "WARNING",
                "propagate": True,
            },
            "telegram.ext": {
                "level": "WARNING",
                "propagate": True,
            },
            "src.bot": {
                "level": "DEBUG",
                "propagate": True,
            },
        },
    }

    logging.config.dictConfig(config)

    # Set up exception hook to log uncaught exceptions
    def handle_exception(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            # Don't log keyboard interrupt
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return

        logger = logging.getLogger(__name__)
        logger.critical(
            "Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback)
        )

    sys.excepthook = handle_exception

    # Log startup message
    logging.getLogger(__name__).info(f"Logging configured. Log file: {log_file}")


class TelegramFilter(logging.Filter):
    """Filter to exclude repetitive Telegram-related log messages."""

    def filter(self, record):
        # Skip getUpdates messages completely
        if "getUpdates" in record.getMessage():
            return False

        # Skip repetitive HTTP Request messages
        if "HTTP Request: " in record.getMessage():
            # Only show if it's not a polling request
            return "getUpdates" not in record.getMessage()

        # Allow all other messages
        return True


def log_exception(logger, message="An error occurred", exc_info=None):
    """
    Log an exception with traceback.

    Args:
        logger: Logger instance
        message: Message to log
        exc_info: Exception info tuple (type, value, traceback)
    """
    if exc_info:
        logger.error(f"{message}: {exc_info[1]}")
        logger.debug("".join(traceback.format_exception(*exc_info)))
    else:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        logger.error(f"{message}: {exc_value}")
        logger.debug(
            "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
        )
