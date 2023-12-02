"""
Created: 2023-11-19
Author: Gao Tianchi
"""

import logging
import re
from pathlib import Path

from flask import (
    Blueprint,
    abort,
    current_app,
    jsonify,
    make_response,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from myblog.model.database import Category, Comment, Post
from myblog.model.fileitem import OwnerProfile, PostFile
from myblog.model.render import get_render
from myblog.model.validator import get_validator

owner = Blueprint("owner", __name__)

logger = logging.getLogger("controller.owner")


@owner.before_request
def validate_owner() -> None:
    if request.endpoint == "owner.login":
        logger.info("Ready to log in.")
        return None

    if session.get("token"):
        token = session["token"]
        validator = get_validator("token")
        validator.set(token.encode("utf-8"), current_app.config["SECRET_KEY"])
        if validator.validate():
            logger.info("Successfully log in with token in session.")
            return None
        else:
            logger.error("Token in the session is invalid.")

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
    filepath: Path = OwnerProfile.WORKTREE.joinpath(*_filepath[0].split("/"))
    post = PostFile(filepath)

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

    category = Category.create(post.category)
    new_post = Post.create(
        post.title, post.html, category.id, post.author, post.toc, post.summary
    )

    return jsonify(new_post.to_json())


@owner.route("/modify/post", methods=["PATCH"])
def modify_post():
    json_items: dict = request.json
    _filepath: list[str] = json_items.get("path")
    if not _filepath:
        logger.error(f"File path was not found in the json filed.")
        abort(400)

    filepath: Path = OwnerProfile.WORKTREE.joinpath(*_filepath[0].split("/"))
    post = PostFile(filepath)
    old_title_file = post

    if len(_filepath) == 2:
        new_title_file = OwnerProfile.WORKTREE.joinpath(*_filepath[1].split("/"))
        post = PostFile(new_title_file)

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

    category = Category.create(post.category)
    old_post = Post.query.filter_by(title=old_title_file.title).first_or_404()

    old_categroy = old_post.category
    posts_with_same_category: list = old_categroy.posts
    if (old_title_file.title != post.category) and len(posts_with_same_category) == 1:
        logger.info(f"Deleted empty category {old_categroy}.")
        old_categroy.delete()

    new_post = old_post.modify(
        post.title, post.html, category.id, post.author, post.toc, post.summary
    )

    return jsonify(new_post.to_json())


@owner.route("/delete/post", methods=["DELETE"])
def delete_post():
    json_items: dict = request.json
    _filepath: list[str] = json_items.get("path")
    if not _filepath:
        logger.error(f"File path was not found in the json filed.")
        abort(400)
    filepath: Path = OwnerProfile.WORKTREE.joinpath(*_filepath[0].split("/"))
    post = PostFile(filepath)

    old_post = Post.query.filter_by(title=post.title).first_or_404()
    old_categroy = old_post.category
    posts_with_same_category: list = old_categroy.posts
    if len(posts_with_same_category) == 1:
        logger.info(f"Deleted empty category {old_categroy}.")
        old_categroy.delete()
    old_post.delete()

    return jsonify(f"Successfully delete '{post.title}'.")


@owner.route("/login", methods=["GET", "POST"])
def login():
    if request.form:
        api_key: str = request.form.get("api_key")
        if not api_key:
            logger.error("No api key was found.")
            return abort(401)

        validator = get_validator("token")
        validator.set(api_key.encode("utf-8"), current_app.config["SECRET_KEY"])
        if not validator.validate():
            logger.error("Api key is invalid.")
            return abort(401)

        session["token"] = api_key

        return redirect(url_for("owner.manage"))

    return render_template("login.html")


@owner.route("/manage", methods=["GET"])
def manage():
    return render_template("manage.html")


@owner.route("/manage/comment", methods=["GET", "POST"])
def manage_comment():
    page = request.args.get("page", type=int, default=1)
    per_page = current_app.config["COMMENT_PER_PAGE"]
    comments = Comment.query.order_by(Comment.timestamp.desc()).paginate(
        page=page, per_page=per_page
    )
    total_page = Comment.query.count() // per_page + 1
    return render_template(
        "manage-comment.html", comments=comments, page=page, total_page=total_page
    )


@owner.route("/delete/comment/<comment_id>", methods=["POST"])
def delete_comment(comment_id: int):
    comment = Comment.query.get_or_404(comment_id)
    comment.delete()

    return redirect(url_for("owner.manage_comment"))
