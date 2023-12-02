"""
Created: 2023-11-20
Author: Gao Tianchi
"""

import datetime

from dateutil.relativedelta import relativedelta
from flask import Flask

from myblog.utlis import archive_post_by_date, title_to_url

from .command import regisiter_command
from .config import get_config
from .controller import bp_owner, bp_visitor
from .flaskexten import db
from .model.database import Category, Comment, Post
from .model.fileitem import OwnerProfile


def create_app(environment: str = None) -> Flask:
    config = get_config(environment)

    app = Flask(
        __package__,
        static_folder=config.PATH_STATIC,
        template_folder=config.PATH_TEMPLATES,
    )
    app.config.from_object(config)

    db.init_app(app)

    app.register_blueprint(bp_owner)
    app.register_blueprint(bp_visitor)

    regisiter_command(app)

    @app.shell_context_processor
    def make_shell_context():
        return dict(db=db, post=Post, category=Category, comment=Comment)

    @app.context_processor
    def make_global_template_variable():
        return dict(owner=OwnerProfile(), postdb=Post, categorydb=Category)

    @app.context_processor
    def make_global_template_functions():
        return dict(
            archive_post_by_date=archive_post_by_date,
            datetime=datetime,
            relativedelta=relativedelta,
            sorted=sorted,
        )

    @app.template_global()
    def ttu(title: str):
        return title_to_url(title)

    return app
