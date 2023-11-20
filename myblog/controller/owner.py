"""
Created: 2023-11-19
Author: Gao Tianchi
"""

import logging
import re
from pathlib import Path

from flask import Blueprint, abort, current_app, jsonify, redirect, request, url_for

from myblog.definition import Owner, Post
from myblog.model.render import get_render
from myblog.model.validator import validate_token

owner = Blueprint("owner", __name__)

logger = logging.getLogger("controller.owner")


@owner.before_request
def validate_owner() -> None:
    authorization: str | None = request.headers.get("Authorization")
    if not authorization:
        logger.error("Field 'authorization' is not fond in the request headers.")
        return abort(401)

    token: str = re.sub(r"Bearer ", "", authorization)
    if not token:
        logger.error("Token is not fond in the field 'authorization'.")
        return abort(401)

    if not validate_token(token.encode("utf-8"), current_app.config["SECRET_KEY"]):
        logger.error("Invalid token!")
        return abort(401)

    logger.info("Successfully log in.")


@owner.route("/", methods=["POST"])
def hello():
    return jsonify("Hello, world.")


@owner.route("/add/post", methods=["POST"])
def add_post():
    _filepath: str = request.data.decode("utf-8")
    worktree: Path = Owner.PATH_WORKTREE
    filepath = worktree.joinpath(*_filepath.split("/"))
    post = Post(filepath)

    if not post.is_post():
        logger.warning(f"File {filepath} is not a post.")
        return abort(400)

    render = get_render("post")
    post = render(post)

    return jsonify(post)


@owner.route("/modify/post", methods=["PATCH"])
def modify_post():
    _filepath: str = request.data.decode("utf-8")
    worktree: Path = Owner.PATH_WORKTREE
    filepath = worktree.joinpath(*_filepath.split("/"))
    post = Post(filepath)

    if not post.is_post():
        logger.warning(f"File {filepath} is not a post.")
        return abort(400)

    return jsonify(dict(title=post.TITLE, author=post.AUTHOR))


@owner.route("/delete/post", methods=["DELETE"])
def delete_post():
    _filepath: str = request.data.decode("utf-8")
    worktree: Path = Owner.PATH_WORKTREE
    filepath = worktree.joinpath(*_filepath.split("/"))

    return jsonify(dict(filepath=str(filepath)))
