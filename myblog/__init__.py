"""
Abstract: This module defines the main program of the FLASK application, 
and all FLASK-related components are registered to the instance in the factory function.

Author: Gao Tianchi
Contact: 6159984@gmail.com
Version: 0.3
Creation date: 2023-11-02
Latest modified date: 2023-11-02
Copyright (C) 2023 Gao Tianchi
"""

import logging
import os

from flask import Flask

from myblog.config import get_config
from myblog.flaskexten import db
from myblog.model.database.db import Post

config = get_config()
error_logfile = os.path.join(config.PATH_LOG, "error.log")
access_logfile = os.path.join(config.PATH_LOG, "access.log")

logging.basicConfig(
    filename=access_logfile,
    filemode="w",
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(module)s - %(funcName)s- %(message)s",
)

error_logger = logging.getLogger("error")
error_handler = logging.FileHandler(error_logfile, "w", encoding="utf-8")
error_logger.addHandler(error_handler)


def create_app():
    app = Flask(
        __package__,
        static_folder=config.PATH_STATIC,
        template_folder=config.PATH_TEMPLATE,
    )

    app.config.from_object(config)

    db.init_app(app)

    @app.shell_context_processor
    def make_shell_context():
        return dict(db=db, post=Post)

    return app
