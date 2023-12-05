"""
Created: 2023-11-20
Author: Gao Tianchi
"""

import json
import logging
from datetime import datetime

import pytz
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from myblog.flaskexten import db

from .fileitem import PostFile

logger = logging.getLogger("model.database")

from werkzeug.security import check_password_hash, generate_password_hash


class User(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    registered_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    last_login: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    intro: Mapped[str] = mapped_column(String(255), nullable=False)
    profile: Mapped[str] = mapped_column(Text, nullable=True)
    timezone: Mapped[str] = mapped_column(String(255), default="Asia/Shanghai")

    @classmethod
    def create(cls, name, email, password, intro, timezone, profile=None) -> "User":
        password_hash = generate_password_hash(password)
        city_timezone = pytz.timezone(timezone)
        registered_at = datetime.now().astimezone(city_timezone).now()
        new_user = User(
            name=name,
            email=email,
            password_hash=password_hash,
            registered_at=registered_at,
            last_login=registered_at,
            intro=intro,
            profile=profile,
            timezone=timezone,
        )
        db.session.add(new_user)
        db.session.commit()
        return User.query.get(new_user.id)

    def update_information(self, name, email, intro, profile=None, timezone=None):
        self.name = name
        self.email = email
        self.intro = intro
        self.profile = profile
        self.timezone = timezone if timezone else self.timezone

        db.session.add(self)
        db.session.commit()

    def update_activity(self):
        city_timezone = pytz.timezone(self.timezone)
        self.last_login = datetime.now().astimezone(city_timezone).now()
        db.session.add(self)
        db.session.commit()

    def update_password(self, new_password: str):
        self.password_hash = generate_password_hash(new_password)
        db.session.add(self)
        db.session.commit()

    def validate_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    def __repr__(self) -> str:
        return f"<User {self.name}>"


class Post(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(255))
    content: Mapped[str] = mapped_column(Text)
    summary: Mapped[str] = mapped_column(Text, nullable=True)
    toc: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime)
    updated_at: Mapped[datetime] = mapped_column(DateTime)
    published: Mapped[bool] = mapped_column(Boolean)
    published_at: Mapped[datetime] = mapped_column(DateTime)
    slug: Mapped[str] = mapped_column(String(255))
    meta_title: Mapped[str] = mapped_column(String(255))


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
