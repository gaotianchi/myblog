"""
职责：初始化 flask 实例，将系统组件注册到 flask 实例。
"""

import logging
import logging.config

from flask import Flask

from myblog.config import get_config

config = get_config()

logging.config.fileConfig(config.PATH_LOG_CONFIG)

logger = logging.getLogger("root")


def create_app():
    app = Flask(__package__)
    app.config.from_object(config)

    return app
