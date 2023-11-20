"""
Created: 2023-11-19
Author: Gao Tianchi
"""

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

ENVIRONMENT: str | None = os.getenv("ENVIRONMENT")


class Base:
    PATH_ROOT: Path = Path(__file__).parent.parent
    PATH_LOG: Path = PATH_ROOT.joinpath("log")

    SECRET_KEY: bytes = b"C_3IbOmd4L15tDuIY78EUYoZBl_wzF2HmDlkz8Yu0BA="


class Dev(Base):
    ...


class Prod(Base):
    ...


class Test(Base):
    ...


def get_config(environment=None):
    environment = ENVIRONMENT if ENVIRONMENT else environment
    match environment:
        case "production":
            return Prod
        case "testing":
            return Test
        case _:
            return Dev
