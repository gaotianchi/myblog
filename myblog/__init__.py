"""
Abstract: This module defines the main program of the FLASK application, 
and all FLASK-related components are registered to the instance in the factory function.

Author: Gao Tianchi
Contact: 6159984@gmail.com
Version: 0.3
Creation date: 2023-11-02
Copyright (C) 2023 Gao Tianchi
"""

import logging

from flask import Flask

from myblog.config import get_config
from myblog.controller import auth_bp, owner_bp
from myblog.flaskexten import db, login_manager
from myblog.model.database.db import Owner, Post, Site

config = get_config()

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(module)s - %(funcName)s- %(message)s",
)


def create_app():
    app = Flask(
        __package__,
        static_folder=config.PATH_STATIC,
        template_folder=config.PATH_TEMPLATE,
    )

    app.config.from_object(config)

    db.init_app(app)
    login_manager.init_app(app)

    app.register_blueprint(auth_bp)
    app.register_blueprint(owner_bp)

    @app.shell_context_processor
    def make_shell_context():
        return dict(db=db, post=Post, owner=Owner, site=Site)

    return app
