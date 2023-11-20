"""
Created: 2023-11-20
Author: Gao Tianchi
"""

import logging
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from myblog.flaskexten import db

logger = logging.getLogger("model.database")


class Post(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    author: Mapped[str] = mapped_column(String(255), nullable=False)
    created: Mapped[datetime] = mapped_column(DateTime, default=datetime.today())
    modified: Mapped[datetime] = mapped_column(DateTime, default=datetime.today())
    category_id: Mapped[int] = mapped_column(Integer, ForeignKey("category.id"))

    category = relationship("Category", back_populates="posts")

    @classmethod
    def create(cls, title: str, body: str, author: str, category_id: int) -> "Post":
        new_item = Post(title=title, body=body, author=author, category_id=category_id)
        db.session.add(new_item)
        db.session.commit()

        new_item = Post.query.get(new_item.id)
        logger.info(f"Created new post {new_item}.")
        return new_item

    @classmethod
    def modify(cls, title: str, body: str, author: str, category_id: int) -> "Post":
        new_item = Post(
            title=title,
            body=body,
            author=author,
            category_id=category_id,
            modified=datetime.today(),
        )
        db.session.add(new_item)
        db.session.commit()

        new_item = Post.query.get(new_item.id)
        logger.info(f"Modfied new post {new_item}.")
        return new_item

    def delete(self) -> None:
        logger.info(f"Deleted new post {self}.")
        db.session.delete(self)
        db.session.commit()

    def to_json(self) -> str:
        ...

    def __repr__(self) -> str:
        return f"<Post {self.title}>"


class Category(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)

    posts = db.relationship("Post", back_populates="category")
