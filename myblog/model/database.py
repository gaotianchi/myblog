"""
职责：定义数据库表
"""

import base64
import hashlib
from datetime import date

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Date, String, Text
from sqlalchemy.orm import Mapped, mapped_column

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
        self.id = self.generate_id(title)
        self.title = title
        self.body = body
        self.toc = toc
        self.author = author
        self.release = release
        self.updated = updated
        self.summary = summary
        self.category = category

    @staticmethod
    def generate_id(title: str) -> str:
        hash_object = hashlib.md5(title.encode())
        hash_digest = hash_object.digest()

        title_id = base64.urlsafe_b64encode(hash_digest)[:20].decode()

        return title_id
