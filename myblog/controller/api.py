from flask import Blueprint, jsonify, request
from flask.views import MethodView
from flask.wrappers import Response

from myblog.model.database import Post, db

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
        items = self.model.query.all()
        return jsonify([item.to_json() for item in items])

    def post(self):
        item = self.model.from_json(request.json)
        db.session.add(item)
        db.session.commit()
        return jsonify(item.to_json())


api.add_url_rule("/post/<id>", view_func=ItemAPI.as_view("post_item", Post))
api.add_url_rule("/post", view_func=GroupAPI.as_view("post_group", Post))
