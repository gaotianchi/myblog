from flask import Blueprint, current_app, render_template, request
from flask import typing as ft
from flask.views import View

from myblog.model.item import Article, WritingSpace

user = Blueprint("user", __name__)


class Home(View):
    def __init__(self) -> None:
        self.writingspace = WritingSpace(current_app)

    def dispatch_request(self) -> ft.ResponseReturnValue:
        title = request.args.get("title", self.writingspace.home_post_title)
        article = Article(current_app, title)
        return render_template("home.html", article=article)


user.add_url_rule("/", view_func=Home.as_view("home"))
