"""
Created: 2023-11-22
Author: Gao Tianchi
"""

import re

from flask import Blueprint, abort, render_template, request
from sqlalchemy import and_

from myblog.definition import Post
from myblog.model.database import Category as categorydb
from myblog.model.database import Post as postdb

visitor = Blueprint("visitor", __name__)


def get_post_from_url_title(url_title: str):
    url_title = re.sub(r"[^a-zA-Z0-9\-]", "", url_title)
    search_terms = url_title.split("-")
    conditions = [postdb.title.ilike(f"%{term}%") for term in search_terms]
    posts = postdb.query.filter(and_(*conditions)).all()

    if len(posts) > 1 or len(posts) == 0:
        return None

    post_title_words = re.sub(r"[^a-zA-Z0-9]", "", posts[0].title)
    url_words = re.sub(r"[^a-zA-Z0-9]", "", url_title)
    if not url_words == post_title_words.lower():
        return None

    return posts[0]


@visitor.route("/read/post/<url_title>", methods=["GET"])
def read_post(url_title: str):
    post = get_post_from_url_title(url_title)
    if not post:
        return abort(404)

    return render_template("post-detail.html", post=post)


@visitor.route("/archive/post", methods=["GET"])
def archive_post():
    category_name: str = request.args.get("category", Post.CATEGORY_DEFAULT_NAME)
    sort_by: str = request.args.get("sort_by", "newest")

    match sort_by:
        case "oldest":
            sort_method = postdb.modified.asc()
        case _:
            sort_method = postdb.modified.desc()

    category = categorydb.query.filter_by(title=category_name).first_or_404()

    posts = postdb.query.with_parent(category).order_by(sort_method).all()

    return render_template("archive-post.html", posts=posts, category=category)
