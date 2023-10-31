import os
import subprocess

import click
from flask import Flask, render_template
from git import Repo

from myblog.model.database import db


def register_command(app: Flask) -> None:
    @app.cli.command(help="初始化数据库")
    @click.option("--drop", is_flag=True, help="删除旧的数据库表后再创建新表。")
    def initdb(drop):
        if drop:
            click.confirm("确定要删除所有的表吗？", abort=True)
            db.drop_all()
            click.echo("成功删除所有的数据库表。")
        db.create_all()
        click.echo("完成数据库初始化。")

    @app.cli.command(help="初始化用户 git 裸仓库和工作目录")
    def initauthor():
        gitdir: str = app.config["PATH_AUTHOR_GIT_REPO"]
        worktree: str = app.config["PATH_AUTHOR_WORK_REPO"]

        if not gitdir.endswith(".git"):
            raise "必需以 .git 结尾"

        if os.path.exists(gitdir) and os.listdir(gitdir):
            raise f"{gitdir} 已经存在并且非空，请选择其他位置作为 git 裸仓库。"

        if os.listdir(worktree):
            raise f"{worktree} 必须为空！当前 wortree 文件夹不为空。"

        os.makedirs(gitdir)
        os.makedirs(worktree)

        Repo.init(gitdir, bare=True)

        data = dict(
            path_env=os.path.join(app.config["PATH_BASE"], *[".venv", "bin", "python"]),
            path_worktree=worktree,
            path_gitdir=gitdir,
            path_log=os.path.join(app.config["PATH_LOG"], "post-receive.log"),
            secret_key=app.config["SECRET_KEY"],
        )

        target_post_receive: str = os.path.join(gitdir, *["hooks", "post-receive"])

        with open(target_post_receive, "w", encoding="UTF-8") as f:
            f.write(render_template("script/post-receive", data=data))

        subprocess.check_output(["chmod", "a+x", target_post_receive])
