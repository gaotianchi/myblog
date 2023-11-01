"""
职责：初始化 flask 应用
"""

import logging
import os
from logging.handlers import RotatingFileHandler

from flask import Flask

from myblog.model import MySQLHandler
from myblog.model.scheduler import Scheduler
from myblog.model.validator import SettingValidator
from myblog.setting import REQUIRED_CONFIG, config
from myblog.view import api_bp, user_bp


def create_app(name: str = "base"):
    app = Flask("myblog")
    app.config.from_object(config[name])

    validator = SettingValidator(app)
    validator.set(REQUIRED_CONFIG)

    if not validator.validate():
        raise Exception("配置信息缺失")

    Register.register(app)

    return app


class Register:
    @classmethod
    def register(cls, app: Flask):
        cls.app = app

        cls.__register_blueprint(cls)
        cls.__register_logger(cls)
        cls.__register_mysql(cls)
        cls.__register_scheduler(cls)

    def __register_blueprint(cls):
        cls.app.register_blueprint(user_bp)
        cls.app.register_blueprint(api_bp)

    def __register_logger(cls):
        formatter = logging.Formatter(
            "[%(asctime)s]-[%(module)s]-[%(lineno)d]-[%(funcName)s]-[%(levelname)s]-[%(message)s]"
        )
        handler = RotatingFileHandler(
            os.path.join(cls.app.config["PATH_LOG"], "myblog.log"),
            mode="a",
            maxBytes=100 * 1024,
            backupCount=3,
            encoding="UTF-8",
        )
        handler.setFormatter(formatter)
        cls.app.logger.addHandler(handler)
        cls.app.logger.setLevel(logging.DEBUG)

    def __register_mysql(cls):
        mysql_config: dict = cls.app.config["MYSQL_CONFIG"]

        mysql_handler = MySQLHandler(**mysql_config)

        cls.app.config["MYSQL_HANDLER"] = mysql_handler

    def __register_scheduler(cls):
        timer = Scheduler(cls.app)
        timer.run()
