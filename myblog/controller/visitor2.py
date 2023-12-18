"""
Created at: 2023-12-06
Author: Gao Tianchi
"""
import json
from pathlib import Path

from flask import Blueprint, current_app, jsonify

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


@visitor.route("/example", methods=["GET"])
def example():
    example_path: Path = current_app.config["PATH_ROOT"].joinpath("example.txt")
    text: str = example_path.read_text(encoding="utf-8")

    return jsonify(dict(text=text))
