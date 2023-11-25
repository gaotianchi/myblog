"""
Created: 2023-11-20
Author: Gao Tianchi
"""

import json
import logging
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from myblog.definition import Post as PostFile
from myblog.flaskexten import db

logger = logging.getLogger("model.database")


class Post(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(
        String(PostFile.TITLE_MAX_LENGTH), unique=True, nullable=False
    )
    body: Mapped[str] = mapped_column(Text, nullable=False)
    toc: Mapped[str] = mapped_column(Text, nullable=True)
    summary: Mapped[str] = mapped_column(Text, nullable=True)
    author: Mapped[str] = mapped_column(
        String(PostFile.AUTHOR_MAX_LENGTH), nullable=False
    )
    created: Mapped[datetime] = mapped_column(DateTime, default=datetime.today())
    modified: Mapped[datetime] = mapped_column(DateTime, default=datetime.today())
    category_id: Mapped[int] = mapped_column(Integer, ForeignKey("category.id"))

    category = relationship("Category", back_populates="posts")
    comments = relationship("Comment", back_populates="post")

    @classmethod
    def create(
        cls,
        title: str,
        body: str,
        category_id: int,
        author=None,
        toc=None,
        summary=None,
    ) -> "Post":
        old_item = cls.query.filter_by(title=title).first()
        if old_item:
            logger.warning(f"{old_item} already exists, please change the post name.")
            return old_item

        author = author if author else PostFile.AUTHOR_DEFAULT_NAME

        new_item = Post(
            title=title,
            body=body,
            author=author,
            category_id=category_id,
            toc=toc,
            summary=summary,
        )
        db.session.add(new_item)
        db.session.commit()

        new_item = Post.query.get(new_item.id)
        logger.info(f"Created new post {new_item}.")
        return new_item

    def modify(
        self,
        title: str,
        body: str,
        category_id: int,
        author=None,
        toc=None,
        summary=None,
    ) -> "Post":
        self.title = title
        self.body = body
        self.toc = toc
        self.author = author if author else PostFile.author
        self.summary = summary
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
        data = dict(
            id=self.id,
            title=self.title,
            body=self.body,
            author=self.author,
            toc=self.toc,
            summary=self.summary,
            modified=self.modified.isoformat(),
            created=self.created.isoformat(),
            category=self.category.title,
        )

        return json.dumps(data)

    def __repr__(self) -> str:
        return f"<Post {self.title}>"


class Category(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(
        String(PostFile.CATEGORY_MAX_LENGTH), unique=True, nullable=False
    )

    posts = db.relationship("Post", back_populates="category")

    @classmethod
    def create(cls, title: str) -> "Category":
        old_item = cls.query.filter_by(title=title).first()
        if old_item:
            logger.warning(f"{old_item} already exists, old category will be returned.")
            return old_item

        new_item = Category(title=title)

        db.session.add(new_item)
        db.session.commit()

        new_item = Category.query.get(new_item.id)
        logger.info(f"Created new category {new_item}")
        return new_item

    def modify(self, title: str) -> "Category":
        old_item = Category.query.filter_by(title=title).first()
        if old_item:
            logger.warning(
                f"{old_item} already exists, please change the category name."
            )
            return old_item

        if self.title == PostFile.CATEGORY_DEFAULT_NAME:
            logger.warning(f"Can not modify title of default category.")
            return self

        if title == PostFile.CATEGORY_DEFAULT_NAME:
            logger.warning(f"Can not modify {self} to default category.")
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


class Comment(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    from_owner: Mapped[bool] = mapped_column(Boolean, default=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.today())

    post = relationship("Post", back_populates="comments")
    post_id: Mapped[int] = mapped_column(Integer, ForeignKey("post.id"))

    reply_to = relationship("Comment", back_populates="reply_me", remote_side=[id])
    reply_to_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("comment.id"), nullable=True
    )

    reply_me = relationship(
        "Comment", back_populates="reply_to", cascade="all, delete-orphan"
    )

    @classmethod
    def create(cls, content, post_id, reply_to_id=None, from_owner=False) -> "Comment":
        new_item = Comment(
            content=content,
            post_id=post_id,
            reply_to_id=reply_to_id,
            from_owner=from_owner,
        )
        db.session.add(new_item)
        db.session.commit()

        new_item = Comment.query.get(new_item.id)
        logger.info(f"Created new comment {new_item}")
        return new_item

    def modify(self, content) -> "Comment":
        self.content = content

        db.session.add(self)
        db.session.commit()

        new_item = Comment.query.get(self.id)
        logger.info(f"Modified comment {self}")
        return new_item

    def delete(self) -> None:
        logger.info(f"Deleted comment {self}")
        db.session.delete(self)
        db.session.commit()

    def __repr__(self) -> str:
        return f"<Comment {self.id}>"
