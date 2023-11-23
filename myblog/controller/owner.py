"""
Created: 2023-11-19
Author: Gao Tianchi
"""

import json
import logging
import re
from pathlib import Path

from flask import Blueprint, abort, current_app, jsonify, make_response, request

from myblog.definition import Owner, Post
from myblog.model.database import Category as categorydb
from myblog.model.database import Post as postdb
from myblog.model.render import get_render
from myblog.model.validator import get_validator

owner = Blueprint("owner", __name__)

logger = logging.getLogger("controller.owner")


@owner.before_request
def validate_owner() -> None:
    authorization: str | None = request.headers.get("Authorization")
    if not authorization:
        logger.error("Field 'authorization' is not found in the request headers.")
        return abort(401)

    token: str = re.sub(r"Bearer ", "", authorization)
    if not token:
        logger.error("Token is not found in the field 'authorization'.")
        return abort(401)

    validator = get_validator("token")
    validator.set(token.encode("utf-8"), current_app.config["SECRET_KEY"])

    if not validator.validate():
        logger.error("Invalid token!")
        return abort(401)

    logger.info("Successfully log in.")


@owner.route("/add/post", methods=["POST"])
def add_post():
    json_items: dict = request.json
    _filepath: list[str] = json_items.get("path")
    if not _filepath:
        logger.error(f"File path was not found in the json filed.")
        abort(400)
    filepath: Path = Owner.PATH_WORKTREE.joinpath(*_filepath[0].split("/"))
    post = Post(filepath)

    if not post.is_post():
        logger.warning(f"File {filepath} is not a post.")
        return abort(400)

    render = get_render("post")
    post = render(post)

    validator = get_validator("post")
    validator.set(post)

    if not validator.validate():
        message = validator.get_message()
        return abort(make_response(message, 400))

    category = categorydb.create(post.category)
    new_post = postdb.create(post.title, post.body, category.id, post.author, post.toc)

    return jsonify(new_post.to_json())


@owner.route("/modify/post", methods=["PATCH"])
def modify_post():
    json_items: dict = request.json
    _filepath: list[str] = json_items.get("path")
    if not _filepath:
        logger.error(f"File path was not found in the json filed.")
        abort(400)

    filepath: Path = Owner.PATH_WORKTREE.joinpath(*_filepath[0].split("/"))
    post = Post(filepath)
    old_title_file = post

    if len(_filepath) == 2:
        new_title_file = Owner.PATH_WORKTREE.joinpath(*_filepath[1].split("/"))
        post = Post(new_title_file)

    if not post.is_post():
        logger.warning(f"File {filepath} is not a post.")
        return abort(400)

    render = get_render("post")
    post = render(post)

    validator = get_validator("post")
    validator.set(post)

    if not validator.validate():
        message = validator.get_message()
        return abort(make_response(message, 400))

    category = categorydb.create(post.category)
    old_post = postdb.query.filter_by(title=old_title_file.title).first_or_404()

    old_categroy = old_post.category
    posts_with_same_category: list = old_categroy.posts
    if (old_title_file.title != post.category) and len(posts_with_same_category) == 1:
        logger.info(f"Deleted empty category {old_categroy}.")
        old_categroy.delete()

    new_post = old_post.modify(
        post.title, post.body, category.id, post.author, post.toc
    )

    return jsonify(new_post.to_json())


@owner.route("/delete/post", methods=["DELETE"])
def delete_post():
    json_items: dict = request.json
    _filepath: list[str] = json_items.get("path")
    if not _filepath:
        logger.error(f"File path was not found in the json filed.")
        abort(400)
    filepath: Path = Owner.PATH_WORKTREE.joinpath(*_filepath[0].split("/"))
    post = Post(filepath)

    old_post = postdb.query.filter_by(title=post.title).first_or_404()
    old_categroy = old_post.category
    posts_with_same_category: list = old_categroy.posts
    if len(posts_with_same_category) == 1:
        logger.info(f"Deleted empty category {old_categroy}.")
        old_categroy.delete()
    old_post.delete()

    return jsonify(f"Successfully delete '{post.title}'.")
