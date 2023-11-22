"""
Created: 2023-11-22
Author: Gao Tianchi
"""

import re

from flask import Blueprint, abort, jsonify, render_template
from sqlalchemy import and_

from myblog.model.database import Post as postdb

visitor = Blueprint("visitor", __name__)


def title_to_url(title: str) -> str:
    url_title = title.lower().replace(" ", "_")

    url_title = re.sub(r"[^a-zA-Z0-9_]", "", url_title)

    return url_title


def get_post_from_url_title(url_title: str):
    url_title = re.sub(r"[^a-zA-Z0-9_]", "", url_title)
    search_terms = url_title.split("_")
    conditions = [postdb.title.ilike(f"%{term}%") for term in search_terms]
    posts = postdb.query.filter(and_(*conditions)).all()

    if len(posts) > 1 or len(posts) == 0:
        return None

    post_title_words = re.sub(r"[^a-zA-Z0-9]", "", posts[0].title)
    url_words = re.sub(r"[^a-zA-Z0-9]", "", url_title)
    if not url_words == post_title_words.lower():
        print(url_words)
        print(post_title_words)
        return None

    return posts[0]


@visitor.route("/read/post/<url_title>", methods=["GET"])
def read_post(url_title: str):
    post = get_post_from_url_title(url_title)
    if not post:
        return abort(404)

    return render_template("post-detail.html", post=post)
