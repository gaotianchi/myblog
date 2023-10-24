"""
职责：定义应用的稳定配置
被哪些模块使用：
依赖哪些模块：
"""

import os
from datetime import date


class Base:
    """
    职责：定义基本的配置项
    """

    PATH_BASE = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    PATH_LOG = os.path.join(PATH_BASE, "log")

    SCHEDULING_CYCLE_POST = 10
    SCHEDULING_CYCLE_TREND = 10
    REQUIRED_POST_KEY = {"date": date, "summary": str}

    TREND_PUBLISH_SINGAL = "#publish"

    TREND_SUMMARY_MIN_WORD_COUNT = 5
    TREND_SUMMARY_MAX_WORD_COUNT = 72

    TREND_BODY_MIN_WORD_COUNT = 10
    TREND_BODY_MAX_WORD_COUNT = 1000

    REDIS_CONFIG = dict(
        host=os.getenv("REDIS_HOST"),
        max_connections=os.getenv("REDIS_MAX_CONNECTIONS"),
    )

    MYSQL_CONFIG = dict(
        host=os.getenv("MYSQL_HOST"),
        user=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PASSWORD"),
        database=os.getenv("MYSQL_DATABASE"),
    )


config = {"base": Base}
