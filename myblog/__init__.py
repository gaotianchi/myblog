"""
Created: 2023-11-20
Author: Gao Tianchi
"""

import logging

from flask import Flask

from .config import get_config
from .controller import bp_owner
from .flaskexten import db
from .log import console_handler, file_handler
from .model.database import Category, Post

# Set loggers
root = logging.getLogger("root")
root.setLevel(logging.DEBUG)
root.addHandler(file_handler)
root.addHandler(console_handler)


def create_app(environment: str = None) -> Flask:
    config = get_config(environment)

    app = Flask(__package__)
    app.config.from_object(config)

    db.init_app(app)

    app.register_blueprint(bp_owner)

    @app.shell_context_processor
    def make_shell_context():
        return dict(db=db, post=Post, category=Category)

    return app
