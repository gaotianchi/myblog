import redis
from flask import Blueprint, current_app, redirect, render_template, request, url_for

from myblog.model import pool
from myblog.model.item import Author, GitLog, Post

user = Blueprint("user", __name__)

conn = redis.Redis(connection_pool=pool)


@user.route("/read")
def read_post():
    id: str = request.args.get("id")
    post = Post(current_app, id)

    return render_template("page/post.html", post=post)


@user.route("/")
def home():
    s = int(request.args.get("since", 7))
    b = int(request.args.get("before", 0))
    c = int(request.args.get("max_count", 20))

    repo_path: str = current_app.config["GIT_REPO_PATH"]

    author = Author(current_app, since=s, before=b, max_count=c, path=repo_path)

    return render_template("page/home.html", author=author)
