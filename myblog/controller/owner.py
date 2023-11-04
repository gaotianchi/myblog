"""
Abstract: This module defines the owner's view function

Author: Gao Tianchi
Contact: 6159984@gmail.com
Version: 0.3
Creation date: 2023-11-03
Latest modified date: 2023-11-04
Copyright (C) 2023 Gao Tianchi
"""

import json
import logging

from flask import Blueprint, request
from flask_login import login_required

from myblog.flaskexten import db
from myblog.model.database.db import Post

owner_bp = Blueprint("owner", __name__)


logger = logging.getLogger("controller")


@owner_bp.route("/add-post", methods=["POST"])
@login_required
def add_post():
    now_post = Post.insert_from_dict(json.loads(request.json))

    try:
        db.session.add(now_post)
        db.session.commit()
        logger.info(f"Article {now_post} was created successfully.")

        return now_post.to_json()
    except:
        db.session.rollback()
        logger.error(f"Fail to create {now_post}!")

        return "Fail"
