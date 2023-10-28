"""
职责：初始化 flask 实例，将系统组件注册到 flask 实例。
"""
import logging
import logging.config

import click
from flask import Flask

from myblog.config import get_config
from myblog.controller.api import api
from myblog.model.database import Post, db

config = get_config()

logging.config.fileConfig(config.PATH_LOG_CONFIG)

logger = logging.getLogger("root")


def create_app():
    app = Flask(__package__)
    app.config.from_object(config)

    register_extension(app)
    register_blueprint(app)
    register_command(app)
    register_shell_context(app)

    return app


def register_blueprint(app: Flask) -> None:
    app.register_blueprint(api)


def register_extension(app: Flask) -> None:
    db.init_app(app)


def register_command(app: Flask) -> None:
    @app.cli.command(help="初始化数据库")
    @click.option("--drop", is_flag=True, help="删除旧的数据库表后再创建新表。")
    def initdb(drop):
        if drop:
            click.confirm("确定要删除所有的表吗？", abort=True)
            db.drop_all()
            click.echo("成功删除所有的数据库表。")
        db.create_all()
        click.echo("完成数据库初始化。")


def register_shell_context(app: Flask):
    @app.shell_context_processor
    def make_shell_context():
        return dict(db=db, post=Post)
