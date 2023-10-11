import redis
from flask import Blueprint, current_app, redirect, render_template, request, url_for

from myblog.model import pool
from myblog.model.item import GitLog, Post

user = Blueprint("user", __name__)

conn = redis.Redis(connection_pool=pool)


@user.route("/read")
def read_post():
    id: str = request.args.get("id")
    post = Post(current_app, id)

    return render_template("page/post.html", post=post)


@user.route("/")
def home():
    s = request.args.get("s", 7)
    b = request.args.get("b", 0)
    repo_path: str = current_app.config["GIT_REPO_PATH"]

    logs = GitLog(repo_path, s=s, b=b).log

    return render_template("page/home.html", logs=logs)
