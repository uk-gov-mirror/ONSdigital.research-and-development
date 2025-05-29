import logging

# Add a custom logging level for success messages
SUCCESS_LEVEL_NUM = 25  # Between INFO (20) and WARNING (30)
logging.addLevelName(SUCCESS_LEVEL_NUM, "SUCCESS")


# Define a custom logging method for success messages
# Here we are adding a method to the logging.Logger class
def success(self, message, *args, **kwargs):
    if self.isEnabledFor(SUCCESS_LEVEL_NUM):
        self._log(SUCCESS_LEVEL_NUM, message, args, **kwargs)


# Patch the logging.Logger class to include the new success method (monkey patching)
logging.Logger.success = success


class CustomFormatter(logging.Formatter):
    """Define logging formatter with colors for different log levels."""

    dark_grey = "\x1b[90m"
    grey = "\x1b[38;20m"
    yellow = "\x1b[33;20m"
    green = "\x1b[32;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    format = "%(asctime)s - %(levelname)s - %(message)s"

    FORMATS = {
        logging.DEBUG: dark_grey + format + reset,
        logging.INFO: grey + format + reset,
        SUCCESS_LEVEL_NUM: green + format + reset,
        logging.WARNING: yellow + format + reset,
        logging.ERROR: red + format + reset,
        logging.CRITICAL: bold_red + format + reset,
    }

    def format(self, record):
        """Set color formatting for logger."""
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt, datefmt="%Y-%m-%d - %H:%M:%S")
        formatted = formatter.format(record)
        return formatted


def logger_creator(config):
    """Set up logging with a custom formatter for console output."""
    logger = logging.getLogger()
    log_level = config["dev_global"]["logging_level"]
    logger.setLevel(log_level)

    # Remove any existing handlers
    logger.handlers.clear()

    # File handler (with default formatter)
    file_handler = logging.FileHandler("logs/main.log", mode="w")
    file_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(funcName)s - %(levelname)s:%(message)s"
    )
    file_handler.setFormatter(file_formatter)

    # Console handler (with custom color formatter)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(CustomFormatter())
    console_handler.setLevel(log_level)
    console_handler.terminator = "\n"

    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger
