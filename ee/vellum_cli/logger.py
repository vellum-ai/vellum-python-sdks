import logging
import os
from typing import Optional


class CLIFormatter(logging.Formatter):
    grey = "\x1b[38;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    white = "\33[37m"
    reset = "\x1b[0m"
    message_format = "%(message)s"

    FORMATS = {
        logging.DEBUG: white + message_format + reset,
        logging.INFO: grey + message_format + reset,
        logging.WARNING: yellow + message_format + reset,
        logging.ERROR: red + message_format + reset,
        logging.CRITICAL: bold_red + message_format + reset,
    }

    def format(self, record: logging.LogRecord) -> str:
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


def load_cli_logger() -> logging.Logger:
    logger = logging.getLogger(__package__)
    logger.setLevel(os.getenv("LOG_LEVEL", logging.INFO))

    handler = logging.StreamHandler()
    handler.setFormatter(CLIFormatter())
    logger.addHandler(handler)

    return logger


def handle_cli_error(logger: logging.Logger, title: str, message: str, suggestion: Optional[str] = None):
    logger.error("\n\033[1;31m✖ {}\033[0m".format(title))  # Bold red X and title
    logger.error("\n\033[1m{}\033[0m".format(message))  # Bold message
    if suggestion:
        logger.error("\n\033[1;34mNext steps:\033[0m")  # Bold blue
        logger.error(suggestion)

    exit(1)
