import redis
from flask import Blueprint, current_app, redirect, render_template, request, url_for

from myblog.model import pool
from myblog.model.item import Post

user = Blueprint("user", __name__)

conn = redis.Redis(connection_pool=pool)


@user.route("/read")
def read_post():
    id: str = request.args.get("id")
    post = Post(current_app, id)

    return render_template("page/post.html", post=post)


@user.route("/")
def home():
    try:
        recent_post_id: bytes = conn.zrange("post:recent", 0, -1)[0]

        return redirect(url_for(".read_post", id=recent_post_id.decode()))
    except:
        return "还没有发布文章"
