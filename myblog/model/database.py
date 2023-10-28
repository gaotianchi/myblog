"""
职责：定义数据库表
"""
import json
from abc import ABC, abstractmethod
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

    def update_from_json(self, data: str) -> None:
        data_dict: dict = json.loads(data)
        self.id = generate_id(data_dict["title"])
        self.title = data_dict["title"]
        self.body = data_dict["body"]
        self.toc = data_dict["toc"]
        self.author = data_dict["author"]
        self.release = date.fromisoformat(data_dict["release"])
        self.updated = date.fromisoformat(data_dict["updated"])
        self.summary = data_dict["summary"]
        self.category = data_dict["category"]
