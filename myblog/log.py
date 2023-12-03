"""
Summary: Configure the logging system.
Created: 2023-11-19
Author: Gao Tianchi
"""

import logging

from .config import get_config

config = get_config()

# Set formatters
default_formatter = logging.Formatter(
    "%(asctime)s-[%(levelname)s]-[%(module)s]-[%(lineno)d]-[%(name)s]-%(message)s"
)

# Set handlers
file_handler = logging.FileHandler(config.PATH_LOG.joinpath("app.log"), mode="w")
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(default_formatter)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(default_formatter)

# Set loggers
root = logging.getLogger("root")
root.setLevel(logging.DEBUG)
root.addHandler(file_handler)
root.addHandler(console_handler)
