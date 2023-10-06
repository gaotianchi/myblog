import logging
import os
import shutil
from logging.handlers import RotatingFileHandler

import click
import redis
from flask import Flask

from myblog.model import pool
from myblog.model.scheduler import Scheduler
from myblog.setting import config
from myblog.view import api, user


def create_app(config_name: str = "development"):
    app = Flask("myblog")
    app.config.from_object(config[config_name])

    Register.register(app)

    return app


class Register:
    @classmethod
    def register(cls, app: Flask):
        cls.app = app

        cls.__register_blueprint(cls)
        cls.__register_logger(cls)
        cls.__register_command(cls)
        cls.__register_scheduler(cls)

    def __register_logger(cls):
        formatter = logging.Formatter(
            "[%(asctime)s]-[%(module)s]-[%(lineno)d]-[%(funcName)s]-[%(levelname)s]-[%(message)s]"
        )
        handler = RotatingFileHandler(
            os.path.join(cls.app.config["LOG_DIR"], "myblog.log"),
            mode="a",
            maxBytes=100 * 1024,
            backupCount=3,
            encoding="UTF-8",
        )
        handler.setFormatter(formatter)
        cls.app.logger.addHandler(handler)
        cls.app.logger.setLevel(logging.DEBUG)

    def __register_blueprint(cls):
        cls.app.register_blueprint(api.api)
        cls.app.register_blueprint(user.user)

    def __register_scheduler(cls):
        with cls.app.app_context():
            scheduler = Scheduler(cls.app)
            scheduler.run()

    def __register_command(cls):
        @cls.app.cli.command(help="清除数据库中的所有数据.")
        def init():
            click.confirm("确定要清除所有数据吗？(包括 redis 数据库和文件夹中的数据)")

            conn = redis.Redis(connection_pool=pool)

            conn.flushall()
            click.echo("成功清除 redis 中的所有数据!")

            path = cls.app.config["POSTSPACE"]
            shutil.rmtree(path)
            os.mkdir(path)

            click.echo("成功将文件夹中的数据全部删除.")
