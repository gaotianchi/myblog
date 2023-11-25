"""
Created: 2023-11-20
Author: Gao Tianchi
"""

import datetime
import os
import re
import shutil
import subprocess
from collections import defaultdict
from pathlib import Path

import click
from dateutil.relativedelta import relativedelta
from flask import Flask, render_template

from myblog.definition import Owner

from .config import get_config
from .controller import bp_owner, bp_visitor
from .flaskexten import db
from .log import root as logger
from .model.database import Category, Comment, Post


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
        return dict(db=db, post=Post, category=Category, comment=Comment)

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

            for post in posts:
                year = post.created.year
                month = post.created.month

                month_posts = archive[year].get(month, [])
                month_posts.append(post)
                archive[year][month] = month_posts

            return archive

        return dict(
            title_to_url=title_to_url,
            archive_post_by_date=archive_post_by_date,
            datetime=datetime,
            relativedelta=relativedelta,
            sorted=sorted,
        )

    @app.cli.command("forge", help="Generate fake data.")
    @click.option("--category", default=5, help="Generate fake comments.")
    @click.option("--post", default=50, help="Generate fake comments.")
    @click.option("--comment", default=100, help="Generate fake comments.")
    def forge(category: int, post: int, comment: int):
        from myblog.fakes import fake_categories, fake_comments, fake_posts

        db.drop_all()
        db.create_all()

        fake_categories(category)
        click.echo(f"Generated {category} categories.")

        fake_posts(post)
        click.echo(f"Generated {post} posts.")

        fake_comments(comment)
        click.echo(f"Generated {comment} comments")

        click.echo("Done.")

    @app.cli.command("initowner", help="Init user's gitdir and worktree.")
    def initowner():
        owner = Owner()

        GITDIR = owner.PATH_GITDIR
        WORKTREE = owner.PATH_GITDIR
        POST_RECEIVE = GITDIR.joinpath("hooks", "post-receive")

        if Path.exists(GITDIR):
            shutil.rmtree(GITDIR)
            os.mkdir(GITDIR)
        if Path.exists(WORKTREE):
            shutil.rmtree(WORKTREE)
            os.mkdir(WORKTREE)

        # Create remote git repo.
        try:
            cmd_create_remote_repo: str = f"git init --bare {GITDIR}"
            subprocess.run(cmd_create_remote_repo, shell=True, check=True)
            logger.info("Successfully created remote git repository.")
        except subprocess.CalledProcessError as e:
            logger.error(
                f"Fail to created remote git repository with error code {e.returncode}: {e.output}"
            )

        hook_data = render_template("post-receive", gitdir=GITDIR, worktree=WORKTREE)
        with open(POST_RECEIVE, "w") as f:
            f.write(hook_data)

        try:
            cmd_make_post_receive_executable: str = f"chmod +x {POST_RECEIVE}"
            subprocess.run(cmd_make_post_receive_executable, shell=True, check=True)
            logger.info("Successfully make post-receive executable.")
        except subprocess.CalledProcessError as e:
            logger.error(
                f"Fail to make post-receive executable with error code {e.returncode}: {e.output}."
            )

    return app
