"""
Created at: 2023-12-06
Author: Gao Tianchi
"""


from flask import Blueprint, g, jsonify, request

from myblog.model.database import Category, Post

author = Blueprint("author", __name__)


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


@author.route("/update/category/<id>", methods=["PATCH"])
def update_category(id: int):
    form = request.form
    title = form.get("title")
    slug = form.get("slug")
    meta_title = form.get("meta_title")
    content = form.get("content")

    category = Category.query.get(id)
    category.update(
        title=title,
        slug=slug,
        meta_title=meta_title,
        content=content,
    )

    return jsonify(f"Updated category {category.title}."), 200


@author.route("/update/post/<id>", methods=["PATCH"])
def update_post(id: int):
    form = request.form
    title = form.get("title")
    content = form.get("content")
    published = form.get("published", type=bool)
    slug = form.get("slug")
    meta_title = form.get("meta_title")
    author = g.user
    category = Category.query.filter_by(title=form.get("category")).first()
    summary = form.get("summary")
    toc = form.get("toc")

    post = Post.query.get(id)
    post.update(
        title=title,
        content=content,
        published=published,
        slug=slug,
        meta_title=meta_title,
        author=author,
        category=category,
        summary=summary,
        toc=toc,
    )

    return jsonify(f"Updated post {post.title}"), 200


@author.route("/add/post", methods=["POST"])
def add_post():
    form = request.form
    title = form.get("title")
    content = form.get("content")
    published = form.get("published", type=bool)
    slug = form.get("slug")
    meta_title = form.get("meta_title")
    author = g.user
    category = Category.query.filter_by(title=form.get("category")).first()
    summary = form.get("summary")
    toc = form.get("toc")

    new_post = Post.create(
        title=title,
        content=content,
        published=published,
        slug=slug,
        meta_title=meta_title,
        author=author,
        category=category,
        summary=summary,
        toc=toc,
    )

    return jsonify(f"Created post {new_post.title}"), 201


@author.route("/delete/post/<id>", methods=["DELETE"])
def delete_post(id: int):
    post = Post.query.get(id)
    title = post.title
    post.delete()
    return jsonify(f"Deleted post {title}."), 200


@author.route("/delete/category/<id>", methods=["DELETE"])
def delete_category(id: int):
    category = Category.query.get(id)
    title = category.title
    category.delete()
    return jsonify(f"Deleted category {title}."), 200
