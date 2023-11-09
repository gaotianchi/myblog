"""
Abstract: This module defines the visitor's view function

Author: Gao Tianchi
Contact: 6159984@gmail.com
Version: 0.3
Creation date: 2023-11-03
Copyright (C) 2023 Gao Tianchi
"""

import logging

from flask import Blueprint, jsonify, request

from myblog.model.database.db import Post

visitor_bp = Blueprint("visitor", __name__)


logger = logging.getLogger()


@visitor_bp.route("/read/post", methods=["GET"])
def read_post():
    post_id: str = request.args.get("id")
    post = Post.query.get(post_id)
    data = post.to_json()

    return jsonify(data)
