from flask import Blueprint, jsonify, request
from flask.views import MethodView
from flask.wrappers import Response

from myblog.model.database import db

api = Blueprint("api", __name__, subdomain="api")


class ItemAPI(MethodView):
    init_every_request = False

    def __init__(self, model):
        self.model = model
        self.validator = ""

    def _get_item(self, id):
        return self.model.query.get_or_404(id)

    def get(self, id) -> Response:
        item = self._get_item(id)

        return jsonify(item.to_json())

    def patch(self, id) -> Response:
        item = self._get_item(id)

        item.update_from_json(request.json)
        db.session.commit()

        return jsonify(item.to_json())

    def delete(self, id) -> Response:
        item = self._get_item(id)
        db.session.delete(item)
        db.session.commit()
        return "", 204


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
