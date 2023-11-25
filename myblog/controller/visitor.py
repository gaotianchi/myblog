"""
Created: 2023-11-22
Author: Gao Tianchi
"""

import logging
import re
from datetime import datetime, timedelta

from flask import (
    Blueprint,
    abort,
    make_response,
    redirect,
    render_template,
    request,
    url_for,
)
from sqlalchemy import and_

from myblog.definition import Owner, Post
from myblog.model.database import Category as categorydb
from myblog.model.database import Comment
from myblog.model.database import Post as postdb
from myblog.model.render import get_render

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


@visitor.route("/read/post/<post_id>", methods=["GET", "POST"])
def read_post(post_id: int):
    post = postdb.query.get_or_404(post_id)

    if request.form:
        comment_content = request.form.get("comment-area")
        render = get_render("comment")
        comment_content = render(comment_content)
        reply_to_id = request.args.get("reply_to", type=int)
        new_comment = Comment.create(comment_content, post.id, reply_to_id)
        return redirect(
            url_for("visitor.read_post", post_id=post_id) + f"#comment-{new_comment.id}"
        )

    comments = Comment.query.with_parent(post).order_by(Comment.timestamp.desc()).all()

    return render_template("post-detail.html", post=post, comments=comments)


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


@visitor.route("/rss", methods=["GET"])
def rss():
    posts = postdb.query.order_by(postdb.created.desc()).all()

    content = render_template("rss.xml", posts=posts)
    response = make_response(content)
    response.headers["Content-Type"] = "application/rss+xml"

    return response
