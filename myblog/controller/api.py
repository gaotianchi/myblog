from flask import Blueprint
from flask.views import MethodView

api = Blueprint("api", __name__, subdomain="api")


from flask.views import MethodView


class ItemAPI(MethodView):
    init_every_request = False

    def __init__(self, model):
        self.model = model

    def _get_item(self, id):
        ...

    def get(self, id):
        ...

    def patch(self, id):
        ...

    def delete(self, id):
        ...


class GroupAPI(MethodView):
    init_every_request = False

    def __init__(self, model):
        self.model = model

    def get(self):
        ...

    def post(self):
        ...


def register_api(app: Blueprint, model, name):
    item = ItemAPI.as_view(f"{name}-item", model)
    group = GroupAPI.as_view(f"{name}-group", model)
    app.add_url_rule(f"/{name}/<int:id>", view_func=item)
    app.add_url_rule(f"/{name}/", view_func=group)
