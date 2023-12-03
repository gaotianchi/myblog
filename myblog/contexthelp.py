"""
Summary: Define some variables and functions that apply to the context.
Created: 2023-12-03
Author: Gao Tianchi
"""


import datetime

from dateutil.relativedelta import relativedelta
from flask import Flask

from myblog.utlis import archive_post_by_date, title_to_url

from .flaskexten import db
from .model.database import Category, Comment, Post
from .model.fileitem import OwnerProfile, PostFile


def register_context_processor(app: Flask):
    @app.shell_context_processor
    def make_shell_context():
        return dict(
            db=db,
            Category=Category,
            Comment=Comment,
            Post=Post,
            OwnerProfile=OwnerProfile,
            PostFile=PostFile,
        )

    @app.context_processor
    def make_template_context():
        return dict(
            archive_post_by_date=archive_post_by_date,
            datetime=datetime,
            relativedelta=relativedelta,
            sorted=sorted,
            ttu=title_to_url,
            owner=OwnerProfile(),
            postdb=Post,
            categorydb=Category,
        )
