"""
Abstract: This module is used to define and manage application configuration information.

Author: Gao Tianchi
Contact: 6159984@gmail.com
Version: 0.3
Creation date: 2023-11-02
Latest modified date: 2023-11-02
Copyright (C) 2023 Gao Tianchi
"""

import os
import secrets


class BaseConfig:
    SECRET_KEY: str = secrets.token_urlsafe(23)
    TOKEN_EXPRIATION: int = 3600
    PATH_BASE: str = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    PATH_LOG: str = os.path.join(PATH_BASE, "log")
    PATH_STATIC: str = os.path.join(PATH_BASE, *["myblog", "view", "static"])
    PATH_TEMPLATE: str = os.path.join(PATH_BASE, *["myblog", "view", "templates"])


class DevelopmentConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI: str = os.getenv("DEV_SQLALCHEMY_DATABASE_URI")


class TestingConfig(BaseConfig):
    ...


class ProductionConfig(BaseConfig):
    ...


def get_config():
    match os.getenv("ENVIRONMENT"):
        case "development":
            return DevelopmentConfig
        case "testing":
            return TestingConfig
        case "production":
            return ProductionConfig
        case _:
            return DevelopmentConfig
