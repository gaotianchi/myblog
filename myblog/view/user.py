from flask import Blueprint, current_app, render_template, request

from myblog.model.pageitem import HomePage, PostPage

user = Blueprint("user", __name__)


@user.route("/")
def index():
    """
    职责：渲染主页页面
    """
    homepage = HomePage(current_app)
    data = homepage.data

    return render_template("page/home.html", data=data)


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
