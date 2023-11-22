"""
Created: 2023-11-19
Author: Gao Tianchi
"""

import os
import sys
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

ENVIRONMENT: str | None = os.getenv("ENVIRONMENT")
WIN = sys.platform.startswith("win")
if WIN:
    prefix = "sqlite:///"
else:
    prefix = "sqlite:////"


class Base:
    PATH_ROOT: Path = Path(__file__).parent.parent
    PATH_LOG: Path = PATH_ROOT.joinpath("log")

    SECRET_KEY: bytes = b"C_3IbOmd4L15tDuIY78EUYoZBl_wzF2HmDlkz8Yu0BA="


class Dev(Base):
    SQLALCHEMY_DATABASE_URI: str = prefix + str(Base.PATH_ROOT.joinpath("data-dev.db"))
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = True


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
