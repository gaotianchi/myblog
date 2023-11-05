"""
Abstract: This module defines methods for operating database tables.

Required: myblog.model.database.table

Author: Gao Tianchi
Contact: 6159984@gmail.com
Version: 0.3
Creation date: 2023-11-02
Copyright (C) 2023 Gao Tianchi
"""

import json
import logging
import secrets
from datetime import date, datetime

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from myblog.flaskexten import db
from myblog.help import get_post_id, serialize_datetime

from .table import CategoryTable, OwnerTable, PostTable, SiteTable

logger = logging.getLogger("Model.db")


class Site(SiteTable):
    ...


class Owner(OwnerTable, UserMixin):
    def __init__(self, name: str = None) -> None:
        if not name:
            name = "Gao Tianchi"

        self.name = name

    def get_id(self):
        return self.name

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)
        db.session.add(self)
        db.session.commit()

    def validate_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self) -> str:
        return f"<Owner {self.name}>"


class Category(CategoryTable):
    default_name = "uncategorized"

    def __init__(self, name: str = None) -> None:
        if not name:
            name = self.default_name

        self.name = name

    @classmethod
    def create(cls, name: str = None) -> "Category":
        if not name:
            name = cls.default_name

        item = cls(name=name)
        db.session.add(item)
        db.session.commit()

        return Category.query.filter_by(name=name).first()

    def delete(self) -> None:
        if self.name == self.default_name:
            logger.warning(f"Can not delete default category {self.default_name}!")
            return None

        posts = Post.query.filter_by(category_name=self.name).all()
        for post in posts:
            post.category_name = self.default_name
            db.session.add(post)
        db.session.commit()

        db.session.delete(self)
        db.session.commit()

        return None

    def __repr__(self) -> str:
        return f"<Category {self.name}>"


class Post(PostTable):
    def __init__(
        self,
        title: str,
        body: str,
        toc: str = None,
        summary: str = None,
        category: str = None,
    ) -> None:
        self.id = get_post_id(title)
        self.title = title
        self.body = body
        self.toc = toc
        self.summary = summary
        self.release = datetime.now()
        self.updated = datetime.now()

        author = Owner.query.first()
        self.author_name = author.name

        category = category if category else Category.default_name

        item = Category.query.filter_by(name=category).first()
        if not item:
            item = Category.create(category)

        self.category_name = category

    @classmethod
    def create(cls, data: dict) -> "Post":
        post = cls(
            title=data["title"],
            body=data["body"],
            category=data.get("category"),
            toc=data.get("toc"),
            summary=data.get("summary"),
        )

        db.session.add(post)
        db.session.commit()

        return Post.query.filter_by(title=data["title"]).first()

    def update(self, data: dict) -> None:
        self.title = data.get("title", self.title)
        self.id = get_post_id(self.title)
        self.body = data.get("body", self.body)
        self.summary = data.get("summary", self.summary)
        self.updated = datetime.now()
        self.toc = data.get("toc", self.toc)

        category = data.get("category")
        category = category if category else Category.default_name

        item = Category.query.filter_by(name=category).first()
        if not item:
            item = Category.create(category)

        self.category_name = category

        db.session.add(self)
        db.session.commit()

    def delete(self) -> None:
        category = Category.query.filter_by(name=self.category_name).first()
        db.session.delete(self)
        db.session.commit()

        posts = Post.query.filter_by(category_name=category.name).all()
        if not posts:
            category.delete()

    def __repr__(self) -> str:
        return f"<Post {self.title}>"
