"""
职责：定义应用的所有配置信息
应用范围：系统全局
"""

import os


class BaseConfig:
    """
    职责：定义基础配置
    """

    PATH_BASE = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    PATH_LOG = os.path.join(PATH_BASE, "log")
    PATH_LOG_CONFIG = os.path.join(PATH_BASE, "logging.conf")


class DevConfig(BaseConfig):
    """
    职责：定义开发环境下的配置信息
    """


class TestingConfig(BaseConfig):
    """
    职责：定义测试环境下的配置信息
    """


class ProductionConfig(BaseConfig):
    """
    职责：定义生产环境中的配置信息
    """


def get_config():
    match os.getenv("ENV_CONFIG"):
        case "dev":
            return DevConfig
        case "testing":
            return TestingConfig
        case "production":
            return ProductionConfig
        case _:
            raise Exception("没有检测到配置选项，请在环境")
