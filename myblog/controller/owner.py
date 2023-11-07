"""
Abstract: This module defines the owner's view function

Author: Gao Tianchi
Contact: 6159984@gmail.com
Version: 0.3
Creation date: 2023-11-03
Copyright (C) 2023 Gao Tianchi
"""

import json
import logging
from pathlib import Path

from cryptography.fernet import Fernet
from flask import Blueprint, abort, current_app, g, jsonify, request

from myblog.model.database.db import Owner, Post
from myblog.model.mdrender.itemrender import PostRender

owner_bp = Blueprint("owner", __name__)


logger = logging.getLogger("controller")


def decrypt_token(secret_key: bytes, token: str) -> str:
    fernet = Fernet(secret_key)
    decrypted_data = fernet.decrypt(token.encode("utf-8"))

    return decrypted_data.decode("utf-8")


@owner_bp.before_request
def load_user():
    token: str = request.args.get("token")
    if token:
        try:
            decrypted_data: str = decrypt_token(current_app.config["SECRET_KEY"], token)
            data: dict = json.loads(decrypted_data)
            owner = Owner.query.get(data["name"])
            if owner:
                g.owner = owner
            else:
                raise Exception("Fail to Login!")

            logger.info(f"Login successfully.")
        except:
            logger.info(f"Fail to Login!")
            abort(401)
    else:
        abort(401)

    return None


@owner_bp.route("/add/post", methods=["POST"])
def add_post():
    changed_post_path: str = json.loads(request.json)["path"]
    postdirname: str = Path(current_app.config["PATH_OWNER_POST"]).stem
    summary_length: int = current_app.config["POST_SUMMARY_LENGTH"]

    postrender = PostRender()
    postrender.set(
        changed_post_path,
        postdirname=postdirname,
        summary_length=summary_length,
    )

    data = postrender.data
    title = data["title"]
    body = data["body"]
    logger.info(data)
    if not body:
        logger.warning(f"Post body is required!")
        return f"Post body is required!"

    post = Post.query.filter_by(title=title).first()
    if post:
        logger.warning(f"{post} has been created!")
        return f"{post} has been created!"

    new_post = Post.create(data)

    return jsonify(new_post.to_json())


@owner_bp.route("/update/post", methods=["PATCH"])
def update_post():
    changed_post_path: str = json.loads(request.json)["path"]
    postdirname: str = Path(current_app.config["PATH_OWNER_POST"]).stem
    summary_length: int = current_app.config["POST_SUMMARY_LENGTH"]

    postrender = PostRender()
    postrender.set(
        changed_post_path,
        postdirname=postdirname,
        summary_length=summary_length,
    )

    data = postrender.data
    title = data["title"]
    body = data["body"]
    if not body:
        logger.warning(f"Post body is required!")
        return f"Post body is required!"

    post = Post.query.filter_by(title=title).first()
    if not post:
        logger.warning(f"{post} has not been created!")
        return f"{post} has not been created!"

    post.update(data)

    return jsonify(post.to_json())


@owner_bp.route("/delete/post", methods=["DELETE"])
def delete_post():
    changed_post_path: str = json.loads(request.json)["path"]
    title = Path(changed_post_path).stem

    post = Post.query.filter_by(title=title).first()
    if not post:
        logger.warning(f"{post} has been deleted.")
        return f"{post} has been deleted."

    post.delete()

    return f"{post} has been deleted."
