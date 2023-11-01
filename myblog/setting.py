"""
职责：定义应用的稳定配置
被哪些模块使用：
依赖哪些模块：
"""

import os
from datetime import date

from dotenv import load_dotenv

load_dotenv()

REQUIRED_CONFIG = [
    "GIT_PYTHON_GIT_EXECUTABLE",
    "GIT_PYTHON_REFRESH",
    "PATH_GIT_USERDATA",
    "PATH_WORKTREE_USERDATA",
    "MYSQL_HOST",
    "MYSQL_USER",
    "MYSQL_PASSWORD",
    "MYSQL_DATABASE",
    "PATH_BASE",
    "PATH_LOG",
    "SCHEDULING_CYCLE_POST",
    "SCHEDULING_CYCLE_TREND",
    "REQUIRED_POST_KEY",
    "HOME_RECENT_TREND_COUNT",
    "TREND_PUBLISH_SINGAL",
    "TREND_SUMMARY_MIN_WORD_COUNT",
    "TREND_SUMMARY_MAX_WORD_COUNT",
    "TREND_BODY_MIN_WORD_COUNT",
    "TREND_BODY_MAX_WORD_COUNT",
    "REQUIRED_PROFILE_AUTHOR_KEY",
    "REQUIRED_PROFILE_WEBSITE_KEY",
    "REQUIRED_PRIFILE_CONTENT_KEY",
    "HOME_RECENT_POST_COUNT",
]


class Base:
    """
    职责：定义基本的配置项
    """

    PATH_BASE = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    PATH_LOG = os.path.join(PATH_BASE, "log")

    SCHEDULING_CYCLE_POST = 10
    SCHEDULING_CYCLE_TREND = 10
    REQUIRED_POST_KEY = {"date": date, "summary": str}
    REQUIRED_PROFILE_AUTHOR_KEY = {"name": str, "email": str}
    REQUIRED_PROFILE_WEBSITE_KEY = {
        "title": str,
        "building_time": str,
        "description": str,
    }
    REQUIRED_PRIFILE_CONTENT_KEY = {"trend_repo": list[str]}

    HOME_RECENT_TREND_COUNT = 30
    HOME_RECENT_POST_COUNT = 7

    TREND_PUBLISH_SINGAL = "#publish"

    TREND_SUMMARY_MIN_WORD_COUNT = 5
    TREND_SUMMARY_MAX_WORD_COUNT = 72

    TREND_BODY_MIN_WORD_COUNT = 10
    TREND_BODY_MAX_WORD_COUNT = 1000

    MYSQL_CONFIG = dict(
        host=os.getenv("MYSQL_HOST"),
        user=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PASSWORD"),
        database=os.getenv("MYSQL_DATABASE"),
    )


config = {"base": Base}
