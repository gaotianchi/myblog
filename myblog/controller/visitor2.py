"""
Created at: 2023-12-06
Author: Gao Tianchi
"""
import json

from flask import Blueprint, jsonify

from myblog.model.database import Post
from myblog.utlis import DateTimeEncoder

visitor = Blueprint("visitor", __name__)


@visitor.route("/read/post/<slug>", methods=["GET"])
def read_post(slug: str):
    post = Post.query.filter_by(slug=slug).first()
    if not post:
        return jsonify("No post was found."), 404
    data = json.dumps(post.to_dict(), cls=DateTimeEncoder, indent=4)
    return jsonify(data), 200
