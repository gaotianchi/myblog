"""
Created: 2023-11-20
Author: Gao Tianchi
"""

import logging
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from myblog.flaskexten import db
from myblog.utlis import get_local_datetime

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

    posts = relationship("Post", back_populates="author")

    @classmethod
    def create(cls, name, email, password, intro, timezone, profile=None) -> "User":
        password_hash = generate_password_hash(password)
        registered_at = get_local_datetime(timezone)
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
        self.last_login = get_local_datetime(self.timezone)
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
    published_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    slug: Mapped[str] = mapped_column(String(255))
    meta_title: Mapped[str] = mapped_column(String(255))
    author_id: Mapped[int] = mapped_column(Integer, ForeignKey("author.id"))
    category_id: Mapped[int] = mapped_column(Integer, ForeignKey("category.id"))

    author = relationship("User", back_populates="posts")
    category = relationship("Category", back_populates="posts")


class Category(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(255))
    content: Mapped[str] = mapped_column(Text)
    slug: Mapped[str] = mapped_column(String(255))
    meta_title: Mapped[str] = mapped_column(String(255))

    posts = relationship("Post", back_populates="category")


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
