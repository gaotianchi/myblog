"""
Created: 2023-11-20
Author: Gao Tianchi
"""

from flask import Flask

from .config import get_config
from .controller import bp_owner


def create_app(environment: str = None) -> Flask:
    config = get_config(environment)

    app = Flask(__package__)
    app.config.from_object(config)

    app.register_blueprint(bp_owner)

    return app
