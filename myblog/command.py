"""
Created: 2023-12-03
Author: Gao Tianchi
"""

import logging
import os
import shutil
import subprocess
from pathlib import Path

import click
from flask import Flask, render_template

from .flaskexten import db
from .model.fileitem import OwnerProfile

logger = logging.getLogger("root.command")


def regisiter_command(app: Flask):
    @app.cli.command("initdb", help="Initialize the database.")
    def initdb():
        db.session.rollback()
        db.drop_all()
        db.create_all()

    @app.cli.command("forge", help="Generate fake data.")
    @click.option("--category", default=5, help="Generate fake categories.")
    @click.option("--post", default=50, help="Generate fake posts.")
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
        owner = OwnerProfile()

        GITDIR = owner.GITDIR
        WORKTREE = owner.WORKTREE
        POST_RECEIVE = GITDIR.joinpath("hooks", "post-receive")

        if Path.exists(GITDIR):
            shutil.rmtree(GITDIR)

        if Path.exists(WORKTREE):
            shutil.rmtree(WORKTREE)

        os.mkdir(GITDIR)
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
