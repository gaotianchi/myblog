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

from myblog.model.database import Category, Comment, Post
from myblog.model.render import get_render
from myblog.utlis import title_to_url

visitor = Blueprint("visitor", __name__)

logger = logging.getLogger("controller.visitor")


@visitor.route("/read/post/<post_id>/<post_title>", methods=["GET", "POST"])
def read_post(post_id: int, post_title: str):
    post = Post.query.get_or_404(post_id)
    if not title_to_url(post.title) == post_title:
        abort(404)

    if request.form:
        comment_content = request.form.get("comment-area")
        render = get_render("comment")
        comment_content = render(comment_content)
        reply_to_id = request.args.get("reply_to", type=int)
        new_comment = Comment.create(comment_content, post.id, reply_to_id)
        return redirect(
            url_for(
                "visitor.read_post",
                post_id=post_id,
                post_title=title_to_url(post.title),
            )
            + f"#comment-{new_comment.id}"
        )

    comments = Comment.query.with_parent(post).order_by(Comment.timestamp.desc()).all()

    return render_template("post-detail.html", post=post, comments=comments)


@visitor.route("/")
@visitor.route("/archive/post", methods=["GET"])
def archive_post():
    posts_query = Post.query

    category_name: str = request.args.get("category")
    sort_by: str = request.args.get("sort_by", "newest")

    from_date: str = request.args.get("from")
    to_date: str = request.args.get("to")
    t = timedelta()

    match sort_by:
        case "oldest":
            sort_method = Post.modified.asc()
        case _:
            sort_method = Post.modified.desc()

    posts_query = posts_query.order_by(sort_method)

    if category_name:
        category_name = re.sub("-", " ", category_name)
        category = Category.query.filter_by(title=category_name).first()
        if category:
            posts_query = posts_query.with_parent(category)
        else:
            return abort(400)

    date_pattern = re.compile(r"\d{4}-\d{2}-\d{2}")
    if from_date:
        m_1 = re.match(date_pattern, from_date)
        if m_1:
            f_date = datetime.fromisoformat(m_1.group(0))
            posts_query = posts_query.filter(Post.created >= f_date)
        else:
            abort(400)

    if to_date:
        m_2 = re.match(date_pattern, to_date)
        if m_2:
            t_date = datetime.fromisoformat(m_2.group(0))
            posts_query = posts_query.filter(Post.created < t_date)
        else:
            abort(400)

    posts = posts_query.all()

    return render_template("archive-post.html", posts=posts)


@visitor.route("/rss", methods=["GET"])
def rss():
    posts = Post.query.order_by(Post.created.desc()).all()

    content = render_template("rss.xml", posts=posts)
    response = make_response(content)
    response.headers["Content-Type"] = "application/rss+xml"

    return response
