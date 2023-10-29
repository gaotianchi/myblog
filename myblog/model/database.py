"""
职责：
"""
import json
from datetime import date

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Date, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from myblog.utlis import generate_id, json_serial

db = SQLAlchemy()


class Post(db.Model):
    id: Mapped[str] = mapped_column(String(20), primary_key=True)
    title: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    toc: Mapped[str] = mapped_column(Text, nullable=False)
    author: Mapped[str] = mapped_column(String(50), nullable=False)
    release: Mapped[date] = mapped_column(Date, default=date.today())
    updated: Mapped[date] = mapped_column(Date, default=date.today())
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str] = mapped_column(String(30), nullable=False)

    def __init__(self, title, body, toc, author, release, updated, summary, category):
        self.id = generate_id(title)
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

        return json.dumps(data, ensure_ascii=False, default=json_serial)

    def update_from_json(self, data: dict) -> None:
        """
        在当前情况下，修改标题后文章的 ID 会发生变化。
        """
        self.title = data.get("title", self.title)
        self.id = generate_id(self.title)
        self.body = data.get("body", self.body)
        self.toc = data.get("toc", self.toc)
        self.author = data.get("author", self.author)
        self.release = date.fromisoformat(data.get("release", self.release.isoformat()))
        self.updated = date.fromisoformat(data.get("updated", self.updated.isoformat()))
        self.summary = data.get("summary", self.summary)
        self.category = data.get("category", self.category)

    @classmethod
    def from_json(cls, data):
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
