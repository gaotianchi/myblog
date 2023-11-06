"""
Abstract: This module is used to define and manage application configuration information.

Author: Gao Tianchi
Contact: 6159984@gmail.com
Version: 0.3
Creation date: 2023-11-02
Copyright (C) 2023 Gao Tianchi
"""

import os

from cryptography.fernet import Fernet


class BaseConfig:
    SECRET_KEY: bytes = Fernet.generate_key()
    PATH_BASE: str = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    PATH_LOG: str = os.path.join(PATH_BASE, "log")
    PATH_STATIC: str = os.path.join(PATH_BASE, *["myblog", "view", "static"])
    PATH_TEMPLATE: str = os.path.join(PATH_BASE, *["myblog", "view", "templates"])
    PATH_KEY: str = os.path.join(PATH_BASE, "KEY")

    with open(PATH_KEY, "w", encoding="utf-8") as f:
        f.write(SECRET_KEY.decode("utf-8"))


class DevelopmentConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI: str = os.getenv("DEV_SQLALCHEMY_DATABASE_URI")
    PATH_OWNER_GIT_REPO: str = os.getenv("DEV_PATH_OWNER_GIT_REPO")
    PATH_OWNER_WORK_REPO: str = os.getenv("DEV_PATH_OWNER_WORK_REPO")
    PATH_OWNER_POST: str = os.path.join(PATH_OWNER_WORK_REPO, "post")


class TestingConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI: str = os.getenv("TESTING_SQLALCHEMY_DATABASE_URI")
    PATH_OWNER_WORK_REPO: str = os.getenv("TESTING_PATH_OWNER_WORK_REPO")
    PATH_OWNER_POST: str = os.path.join(PATH_OWNER_WORK_REPO, "post")


class ProductionConfig(BaseConfig):
    ...


def get_config(environment: str = None):
    environment = environment if environment else os.getenv("ENVIRONMENT")
    match environment:
        case "development":
            return DevelopmentConfig
        case "testing":
            return TestingConfig
        case "production":
            return ProductionConfig
        case _:
            return DevelopmentConfig
