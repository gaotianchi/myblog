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
from datetime import date, datetime

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from myblog.help import get_post_id, serialize_datetime

from .table import OwnerTable, PostTable, SiteTable


class Site(SiteTable):
    ...


class Owner(OwnerTable, UserMixin):
    def __init__(
        self,
        name: str,
        password_hash: str = None,
        email: str = None,
        about: str = None,
        brith: date = None,
        country: str = None,
    ) -> None:
        self.name = name
        self.password_hash = password_hash
        self.email = email
        self.about = about
        self.brith = brith
        self.country = country

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def validate_password(self, password):
        return check_password_hash(self.password_hash, password)


class Post(PostTable):
    def __init__(
        self,
        title: str,
        body: str,
        author: str,
        summary: str,
        category: str,
        toc: str = None,
        release=datetime.now(),
        updated=datetime.now(),
    ) -> None:
        self.id = get_post_id(title)
        self.title = title
        self.body = body
        self.toc = toc
        self.author = author
        self.release = release
        self.updated = updated
        self.summary = summary
        self.category = category

    def to_json(self) -> str:
        data = dict(
            id=self.id,
            title=self.title,
            body=self.body,
            toc=self.toc,
            author=self.author,
            release=self.release,
            updated=self.updated,
            summary=self.summary,
            category=self.category,
        )
        return json.dumps(data, ensure_ascii=False, default=serialize_datetime)

    def update_from_dict(self, data: dict) -> None:
        self.title = data.get("title", self.title)
        self.body = data.get("body", self.body)
        self.toc = data.get("toc", self.toc)
        self.author = data.get("author", self.author)
        self.updated = datetime.now()
        self.summary = data.get("summary", self.summary)
        self.category = data.get("category", self.category)

        self.id = get_post_id(self.title)

    @classmethod
    def insert_from_dict(cls, data: dict) -> "Post":
        post = cls(
            title=data["title"],
            body=data["body"],
            toc=data.get("toc"),
            author=data["author"],
            summary=data["summary"],
            category=data["category"],
        )

        return post

    def __repr__(self) -> str:
        return f"<Post {self.title}>"
