"""
Abstract: This module defines methods for operating database tables.

Required: myblog.model.database.table

Author: Gao Tianchi
Contact: 6159984@gmail.com
Version: 0.3
Creation date: 2023-11-02
Latest modified date: 2023-11-02
Copyright (C) 2023 Gao Tianchi
"""

import json
from datetime import date

from myblog.help import get_post_id, serialize_datetime

from .table import PostTable


class Post(PostTable):
    def __init__(
        self,
        title: str,
        body: str,
        toc: str,
        author: str,
        release: date,
        updated: date,
        summary: str,
        category: str,
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
        self.release = date.fromisoformat(data.get("release", self.release.isoformat()))
        self.updated = date.fromisoformat(data.get("updated", self.updated.isoformat()))
        self.summary = data.get("summary", self.summary)
        self.category = data.get("category", self.category)

        self.id = get_post_id(self.title)

    @classmethod
    def insert_from_dict(cls, data: dict) -> "Post":
        post = cls(
            title=data["title"],
            body=data["body"],
            toc=data["toc"],
            author=data["author"],
            release=date.fromisoformat(data["release"]),
            updated=date.fromisoformat(data["updated"]),
            summary=data["summary"],
            category=data["category"],
        )

        return post
