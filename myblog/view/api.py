from flask import Blueprint
from flask.views import MethodView

api = Blueprint("api", __name__, subdomain="api")


class PostAPI(MethodView):
    init_every_request = False

    def __init__(self, model):
        self.model = model

    def get(self):
        """
        职责：处理 GET 请求，返回单个文章数据
        """
        ...

    def post(self):
        """
        职责：处理 POST 请求，创建新文章
        """
        ...

    def patch(self):
        """
        职责：处理 PATCH 请求，更新已存在的文章
        """
        ...

    def delete(self):
        """
        职责：处理 DELETE 请求，删除指定文章
        """
        ...
