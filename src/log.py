import logging

from src import config


class LoggingFormatter(logging.Formatter):
    black = "\x1b[30m"
    red = "\x1b[31m"
    green = "\x1b[32m"
    yellow = "\x1b[33m"
    blue = "\x1b[34m"
    gray = "\x1b[38m"
    reset = "\x1b[0m"
    bold = "\x1b[1m"
    colors = {
        logging.DEBUG: gray + bold,
        logging.INFO: blue + bold,
        logging.WARNING: yellow + bold,
        logging.ERROR: red,
        logging.CRITICAL: red + bold,
    }

    def format(self, record: logging.LogRecord, /) -> str:
        log_color = self.colors[record.levelno]
        fmt = (
            "(black){asctime}(reset)"
            " (levelcolor){levelname}(reset)"
            " (green){name}.{funcName}()(reset):"
            " {message}"
        )
        fmt = fmt.replace("(black)", self.black + self.bold)
        fmt = fmt.replace("(reset)", self.reset)
        fmt = fmt.replace("(levelcolor)", log_color)
        fmt = fmt.replace("(green)", self.green + self.bold)
        formatter = logging.Formatter(fmt, "%Y-%m-%d %H:%M:%S", style="{")
        return formatter.format(record)


formatter = LoggingFormatter()

logger = logging.getLogger()
logger.setLevel(config.LOG_LEVEL)

stdout_handler = logging.StreamHandler()
stdout_handler.setLevel(config.LOG_LEVEL)
stdout_handler.setFormatter(formatter)
logger.addHandler(stdout_handler)

logging.getLogger("disnake").setLevel(logging.WARNING)

logger.info("Logging has been initialized")


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
