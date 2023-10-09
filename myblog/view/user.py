from flask import Blueprint, current_app, redirect, render_template, request, url_for

from myblog.model.item import Post

user = Blueprint("user", __name__)


@user.route("/read")
def read_post():
    id: str = request.args.get("id")
    post = Post(current_app, id)

    return render_template("page/post.html", post=post)


@user.route("/")
def home():
    return redirect(url_for(".read_post", id="MUDf060"))
