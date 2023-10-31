"""
职责：定义应用的所有配置信息
应用范围：系统全局
"""

import os

from cryptography.fernet import Fernet


class BaseConfig:
    """
    职责：定义基础配置
    """

    PATH_BASE: str = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    PATH_LOG: str = os.path.join(PATH_BASE, "log")
    PATH_LOG_CONFIG: str = os.path.join(PATH_BASE, "logging.conf")
    PATH_KEY: str = os.path.join(PATH_BASE, "KEY")
    SECRET_KEY: bytes = Fernet.generate_key()

    with open(PATH_KEY, "w", encoding="utf-8") as f:
        f.write(SECRET_KEY.decode("utf-8"))


class DevConfig(BaseConfig):
    """
    职责：定义开发环境下的配置信息
    """

    SQLALCHEMY_DATABASE_URI = os.getenv("DEV_SQLALCHEMY_DATABASE_URI")
    PATH_AUTHOR_GIT_REPO = os.getenv("DEV_PATH_AUTHOR_GIT_REPO")
    PATH_AUTHOR_WORK_REPO = os.getenv("DEV_PATH_AUTHOR_WORK_REPO")

    SERVER_NAME = "127.0.0.1:5000"


class TestingConfig(BaseConfig):
    """
    职责：定义测试环境下的配置信息
    """


class ProductionConfig(BaseConfig):
    """
    职责：定义生产环境中的配置信息
    """


def get_config():
    match os.getenv("ENVIRONMENT"):
        case "dev":
            return DevConfig
        case "testing":
            return TestingConfig
        case "production":
            return ProductionConfig
        case _:
            raise Exception("没有检测到配置选项，请在环境变量中添加 ENV_CONFIG 配置项")
