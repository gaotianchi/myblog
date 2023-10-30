"""
职责：处理由作者发起的请求
备注：每个类源自于作者的行为
"""

from flask import Blueprint, request
from flask import typing as ft
from flask.views import View

author = Blueprint("author", __name__)


class AddPost(View):
    """
    职责：创建新文章
    """

    methods = ["POST"]

    def dispatch_request(self) -> ft.ResponseReturnValue:
        return super().dispatch_request()


class DeletePost(View):
    """
    职责：删除指定文章
    """

    methods = ["DELETE"]

    def dispatch_request(self, id: str) -> ft.ResponseReturnValue:
        return super().dispatch_request()


class UpdatePost(View):
    """
    职责：更新指定文章
    """

    methods = ["PATCH"]

    def dispatch_request(self, id: str) -> ft.ResponseReturnValue:
        return super().dispatch_request()


author.add_url_rule("/author/add-post", AddPost.as_view("add-post"))
author.add_url_rule("/author/delete-post/<id>", DeletePost.as_view("delete-post"))
author.add_url_rule("/author/update-post/<id>", UpdatePost.as_view("update-post"))
