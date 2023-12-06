"""
Created at: 2023-12-06
Author: Gao Tianchi
"""


from flask import Blueprint, abort, g, jsonify, request, session

from myblog.model.database import Category, Post, User

author = Blueprint("author", __name__)


@author.before_request
def load_author():
    # Method 1: load user from session.
    if session.get("user_id"):
        user_id = session.get("user_id")
        user = User.query.get(user_id)
        if not user:
            return jsonify("Invalid user id."), 401
        g.user = user
        return None

    # Method 2: Basic auth.
    if request.authorization:
        email = request.authorization.get("username")
        password = request.authorization.get("password")

        user = User.query.filter_by(email=email).first()
        if not user:
            return jsonify("No user was found."), 401
        if not user.validate_password(password):
            return jsonify("Password was invalid."), 403
        g.user = user
        return None

    # Method 3: Api key.
    if request.headers.get("api"):
        api = request.headers.get("api")

        # Validate this api.
        ...


@author.route("/add/category", methods=["POST"])
def add_category():
    form = request.form
    title = form.get("title")
    slug = form.get("slug")
    meta_title = form.get("meta_title")
    content = form.get("content")
    new_category = Category.create(
        title=title,
        slug=slug,
        meta_title=meta_title,
        content=content,
    )
    return jsonify(f"Created category {new_category.title}"), 201
