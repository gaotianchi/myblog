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

    SCHEDULING_CYCLE = 10
    REQUIRED_POST_KEY = {"date": date, "summary": str}

    MYSQL_CONFIG = dict(
        host=os.getenv("MYSQL_HOST"),
        user=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PASSWORD"),
        database=os.getenv("MYSQL_DATABASE"),
    )


config = {"base": Base}
