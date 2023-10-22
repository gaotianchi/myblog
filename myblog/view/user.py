from flask import Blueprint, current_app, render_template, request

from myblog.model.pageitem import PostPage

user = Blueprint("user", __name__)


@user.route("/")
def index():
    return render_template("base.html")


@user.route("/read")
def read_post():
    """
    职责：渲染文章页面
    """

    post_id: str = request.args.get("post")
    postpage = PostPage(current_app)
    postpage.set(post_id)

    data = postpage.data

    return render_template("page/post.html", data=data)
