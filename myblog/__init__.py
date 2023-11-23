"""
Created: 2023-11-20
Author: Gao Tianchi
"""

import datetime
import re
from collections import defaultdict

from dateutil.relativedelta import relativedelta
from flask import Flask

from myblog.definition import Owner

from .config import get_config
from .controller import bp_owner, bp_visitor
from .flaskexten import db
from .log import root as logger
from .model.database import Category, Post


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

    @app.shell_context_processor
    def make_shell_context():
        return dict(db=db, post=Post, category=Category)

    @app.context_processor
    def make_global_template_variable():
        return dict(owner=Owner(), postdb=Post, categorydb=Category)

    @app.context_processor
    def make_global_template_functions():
        def title_to_url(title: str) -> str:
            url_title = title.replace(" ", "-")
            url_title = re.sub(r"[^a-zA-Z0-9\-]", "", url_title)
            return url_title

        def archive_post_by_date(posts: list[Post]) -> dict:
            archive = defaultdict(dict)
            month_posts = defaultdict(list)

            for post in posts:
                year = post.created.year
                month = post.created.month

                if post not in month_posts[month]:
                    month_posts[month].append(post)
                    archive.update({year: month_posts})

            return archive

        return dict(
            title_to_url=title_to_url,
            archive_post_by_date=archive_post_by_date,
            datetime=datetime,
            relativedelta=relativedelta,
        )

    return app
