from flask import Blueprint, current_app, render_template, request
from flask.typing import ResponseReturnValue
from flask.views import View

from myblog.model.item import Article, WritingSpace

api = Blueprint("api", __name__)


class SideBar(View):
    def dispatch_request(self) -> ResponseReturnValue:
        return render_template("_nav.html")


class ArticleView(View):
    def __init__(self) -> None:
        self.writingspace = WritingSpace(current_app)

    def dispatch_request(self) -> ResponseReturnValue:
        title = request.args.get("title", self.writingspace.home_post_title)
        article = Article(current_app, title)
        return render_template("_article.html", article=article)


api.add_url_rule("/nav", view_func=SideBar.as_view("nav"))
api.add_url_rule("/read", view_func=ArticleView.as_view("article"))
