import redis
from flask import Blueprint, current_app, render_template, request

from myblog.model import pool
from myblog.model.item import Home, Post

user = Blueprint("user", __name__)

conn = redis.Redis(connection_pool=pool)


@user.route("/read")
def read_post():
    id: str = request.args.get("id")
    post = Post(current_app, id)

    return render_template("page/post.html", post=post)


@user.route("/")
def home():
    home = Home(current_app)

    return render_template("page/home.html", home=home)
