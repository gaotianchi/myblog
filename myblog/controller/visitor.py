"""
Created: 2023-11-22
Author: Gao Tianchi
"""

import logging
import re
from collections import defaultdict
from datetime import datetime, timedelta

from flask import Blueprint, abort, render_template, request
from sqlalchemy import and_

from myblog.definition import Post
from myblog.model.database import Category as categorydb
from myblog.model.database import Post as postdb

visitor = Blueprint("visitor", __name__)

logger = logging.getLogger("controller.visitor")


def get_post_from_url_title(url_title: str):
    url_title = re.sub(r"[^a-zA-Z0-9\-]", "", url_title)
    search_terms = url_title.split("-")
    conditions = [postdb.title.like(f"%{term}%") for term in search_terms]
    posts = postdb.query.filter(and_(*conditions)).all()

    if len(posts) > 1 or len(posts) == 0:
        return None

    post_title_words = re.sub(r"[^a-zA-Z0-9]", "", posts[0].title)
    url_words = re.sub(r"[^a-zA-Z0-9]", "", url_title)
    if not url_words == post_title_words:
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
    posts_query = postdb.query

    category_name: str = request.args.get("category")
    sort_by: str = request.args.get("sort_by", "newest")

    from_date: str = request.args.get("from")
    to_date: str = request.args.get("to")
    t = timedelta()

    match sort_by:
        case "oldest":
            sort_method = postdb.modified.asc()
        case _:
            sort_method = postdb.modified.desc()

    posts_query = posts_query.order_by(sort_method)

    if category_name:
        category_name = re.sub("-", " ", category_name)
        category = categorydb.query.filter_by(title=category_name).first()
        if category:
            posts_query = posts_query.with_parent(category)
        else:
            return abort(400)

    date_pattern = re.compile(r"\d{4}-\d{2}-\d{2}")
    if from_date:
        m_1 = re.match(date_pattern, from_date)
        if m_1:
            f_date = datetime.fromisoformat(m_1.group(0))
            posts_query = posts_query.filter(postdb.created >= f_date)
        else:
            abort(400)

    if to_date:
        m_2 = re.match(date_pattern, to_date)
        if m_2:
            t_date = datetime.fromisoformat(m_2.group(0))
            posts_query = posts_query.filter(postdb.created < t_date)
        else:
            abort(400)

    posts = posts_query.all()

    return render_template("archive-post.html", posts=posts)
