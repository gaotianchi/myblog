"""
Summary: Configure the logging system.
Created: 2023-11-19
Author: Gao Tianchi
"""

import logging

from config import get_config

config = get_config()

# Set formatters
default_formatter = logging.Formatter(
    "%(asctime)s-[%(levelname)s]-[%(module)s]-[%(lineno)d]-[%(name)s]-%(message)s"
)

# Set handlers
file_handler = logging.FileHandler(config.PATH_LOG.joinpath("app.log"))
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(default_formatter)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(default_formatter)


# Set loggers
def set_logger(
    name, level=logging.DEBUG, handlers=[file_handler, console_handler]
) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(level)
    for handler in handlers:
        logger.addHandler(handler)

    return logger


root = set_logger("root")
controller = set_logger("controller")


def get_logger(name: str = None) -> logging.Logger:
    match name:
        case "controller":
            return controller
        case _:
            return root
