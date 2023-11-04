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
import os
import shutil
import subprocess

import click
from flask import Flask, render_template
from git import Repo

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

    @app.cli.command("create_user", help="test for create user workspace")
    def create_user():
        path_env = os.path.join(config.PATH_BASE, *[".venv", "bin", "python"])

        target_path = os.path.join(
            config.PATH_OWNER_GIT_REPO, *["hooks", "post-receive"]
        )

        target_file = render_template(
            "script/post-receive", path_env=path_env, config=config()
        )

        if os.path.exists(config.PATH_OWNER_GIT_REPO):
            shutil.rmtree(config.PATH_OWNER_GIT_REPO)
        if os.path.exists(config.PATH_OWNER_WORK_REPO):
            shutil.rmtree(config.PATH_OWNER_WORK_REPO)

        os.makedirs(config.PATH_OWNER_GIT_REPO)
        os.makedirs(config.PATH_OWNER_WORK_REPO)

        Repo.init(config.PATH_OWNER_GIT_REPO, bare=True)

        with open(target_path, "w", encoding="utf-8") as f:
            f.write(target_file)

        subprocess.check_output(["chmod", "a+x", target_path])
        subprocess.check_output(["dos2unix", target_path])

        click.echo("Create user workspace successfully.")

    return app
