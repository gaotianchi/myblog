"""
Created: 2023-11-20
Author: Gao Tianchi
"""


from flask import Flask

from .command import regisiter_command
from .config import get_config
from .contexthelp import register_context_processor
from .controller import bp_account, bp_owner, bp_visitor
from .flaskexten import db, mail


def create_app(environment: str = None) -> Flask:
    config = get_config(environment)

    app = Flask(
        __package__,
        static_folder=config.PATH_STATIC,
        template_folder=config.PATH_TEMPLATES,
    )
    app.config.from_object(config)
    db.init_app(app)
    mail.init_app(app)
    app.register_blueprint(bp_owner)
    app.register_blueprint(bp_visitor)
    app.register_blueprint(bp_account)
    regisiter_command(app)
    register_context_processor(app)

    return app
