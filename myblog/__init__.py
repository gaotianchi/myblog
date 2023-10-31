"""
职责：初始化 flask 实例，将系统组件注册到 flask 实例。
"""
import logging
import logging.config

from flask import Flask, request

from myblog.command import register_command
from myblog.config import get_config
from myblog.controller.api import api
from myblog.model.database import Post, db

config = get_config()

logging.config.fileConfig(config.PATH_LOG_CONFIG)

logger = logging.getLogger("root")


def create_app():
    app = Flask(__package__)
    app.config.from_object(config)

    @app.route("/", methods=["POST"])
    def index():
        logger.info(request.data)

        return "hello world"

    register_extension(app)
    register_blueprint(app)
    register_command(app)
    register_shell_context(app)

    return app


def register_blueprint(app: Flask) -> None:
    app.register_blueprint(api)


def register_extension(app: Flask) -> None:
    db.init_app(app)


def register_shell_context(app: Flask):
    @app.shell_context_processor
    def make_shell_context():
        return dict(db=db, post=Post)
