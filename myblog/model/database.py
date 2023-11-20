"""
Created: 2023-11-20
Author: Gao Tianchi
"""

import logging
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from myblog.definition import Post as PostFile
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
    def create(cls, title: str, body: str, category_id: int, author=None) -> "Post":
        author = author if author else PostFile.AUTHOR
        new_item = Post(title=title, body=body, author=author, category_id=category_id)
        db.session.add(new_item)
        db.session.commit()

        new_item = Post.query.get(new_item.id)
        logger.info(f"Created new post {new_item}.")
        return new_item

    def modify(self, title: str, body: str, category_id: int, author=None) -> "Post":
        self.title = title
        self.body = body
        self.author = author if author else PostFile.AUTHOR
        self.category_id = category_id

        self.modified = datetime.today()

        db.session.add(self)
        db.session.commit()

        new_item = Post.query.get(self.id)
        logger.info(f"Modfied post {self}.")
        return new_item

    def delete(self) -> None:
        logger.info(f"Deleted post {self}.")
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

    @classmethod
    def create(cls, title: str) -> "Category":
        new_item = Category(title=title)

        db.session.add(new_item)
        db.session.commit()

        new_item = Category.query.get(new_item.id)
        logger.info(f"Created new category {new_item}")
        return new_item

    def modify(self, title: str) -> "Category":
        if self.title == PostFile.CATEGORY_DEFAULT_NAME:
            logger.warning(f"Can not modify title of default category.")
            return self

        if title == PostFile.CATEGORY_DEFAULT_NAME:
            logger.warning(f"Can modify {self} to default category.")
            return self

        self.title = title

        db.session.add(self)
        db.session.commit()

        new_item = Post.query.get(self.id)
        logger.info(f"Modfied category {self}.")
        return new_item

    def delete(self) -> None:
        default_category_name: str = PostFile.CATEGORY_DEFAULT_NAME
        default_category = Category.query.filter_by(title=default_category_name).first()

        if self.title == default_category_name:
            logger.warning(f"Can not delete default category.{default_category}")
            return None

        for post in self.posts[:]:
            post.category = default_category
            logger.debug(
                f"Category of {post} changed to default category as it's original category {self} was deleted."
            )
            db.session.add(post)

        db.session.commit()
        logger.info(f"Deleted category {self}.")
        db.session.delete(self)
        db.session.commit()

    def __repr__(self) -> str:
        return f"<Category {self.title}>"
