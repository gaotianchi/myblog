from flask import Blueprint, request

from myblog.model.database.db import Post

owner = Blueprint("owner", __name__)


@owner.route("/add-post", methods=["POST"])
def add_post():
    post_data: str = request.json
