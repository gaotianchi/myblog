"""
职责：定义数据库表
"""

from datetime import date

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Date, String, Text
from sqlalchemy.orm import Mapped, mapped_column

db = SQLAlchemy()


class Post(db.Model):
    id: Mapped[str] = mapped_column(String(20), primary_key=True)
    title: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    body: Mapped[str] = mapped_column(Text)
    toc: Mapped[str] = mapped_column(Text)
    author: Mapped[str] = mapped_column(String(50))
    release: Mapped[date] = mapped_column(Date)
    updated: Mapped[date] = mapped_column(Date)
    summary: Mapped[str] = mapped_column(Text)
    category: Mapped[str] = mapped_column(String(30))
