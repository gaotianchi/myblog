"""
Created: 2023-11-20
Author: Gao Tianchi
"""

import logging
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from myblog.flaskexten import db
from myblog.utlis import get_local_datetime, get_username

logger = logging.getLogger("model.database")

from werkzeug.security import check_password_hash, generate_password_hash


class Blog(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(255), default="My personal blog")
    subtitle: Mapped[str] = mapped_column(String(255), default="Record my life.")
    language: Mapped[str] = mapped_column(String(255), default="en-us")
    link: Mapped[str] = mapped_column(String(255), nullable=True)
    description: Mapped[str] = mapped_column(String(255), nullable=True)

    owner = relationship("User", back_populates="blog")

    @classmethod
    def create(cls) -> "Blog":
        new_blog = Blog()
        db.session.add(new_blog)
        db.session.commit()

        return Blog.query.get(new_blog.id)

    def update(
        self, title=None, subtitle=None, language=None, link=None, description=None
    ):
        self.title = title if title else self.title
        self.subtitle = subtitle if subtitle else self.subtitle
        self.language = language if language else self.language
        self.link = link
        self.description = description
        db.session.add(self)
        db.session.commit()
        return Blog.query.get(self.id)

    def delete(self):
        db.session.delete(self)
        db.session.commit()


class User(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255))
    username: Mapped[str] = mapped_column(String(255))
    email: Mapped[str] = mapped_column(String(255))
    password_hash: Mapped[str] = mapped_column(String(255))
    registered_at: Mapped[datetime] = mapped_column(DateTime)
    last_login: Mapped[datetime] = mapped_column(DateTime)
    intro: Mapped[str] = mapped_column(String(255), nullable=True)
    detail: Mapped[str] = mapped_column(Text, nullable=True)
    timezone: Mapped[str] = mapped_column(String(255), default="Asia/Shanghai")
    blog_id: Mapped[int] = mapped_column(Integer, ForeignKey("blog.id"))

    posts = relationship("Post", back_populates="author")
    blog = relationship("Blog", back_populates="owner")

    @classmethod
    def create(
        cls, name, email, password, intro=None, timezone=None, detail=None
    ) -> "User":
        password_hash = generate_password_hash(password)
        timezone = timezone if timezone else "Asia/Shanghai"
        registered_at = get_local_datetime(timezone)
        username = get_username(name)
        blog = Blog.create()
        new_user = User(
            name=name,
            username=username,
            email=email,
            password_hash=password_hash,
            registered_at=registered_at,
            last_login=registered_at,
            intro=intro,
            detail=detail,
            timezone=timezone,
            blog=blog,
        )
        db.session.add(new_user)
        db.session.commit()
        return User.query.get(new_user.id)

    def update_information(
        self, name, username, timezone=None, intro=None, detail=None
    ):
        self.name = name
        self.username = username
        self.intro = intro
        self.detail = detail
        self.timezone = timezone if timezone else self.timezone

        db.session.add(self)
        db.session.commit()

    def delete(self):
        blog_id = self.blog_id
        db.session.delete(self)
        db.session.commit()

        blog = Blog.query.get(blog_id)
        blog.delete()

    def update_activity(self):
        self.last_login = get_local_datetime(self.timezone)
        db.session.add(self)
        db.session.commit()

    def update_email(self, new_email: str):
        self.email = new_email
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
    author_id: Mapped[int] = mapped_column(Integer, ForeignKey("user.id"))
    category_id: Mapped[int] = mapped_column(Integer, ForeignKey("category.id"))

    author = relationship("User", back_populates="posts")
    category = relationship("Category", back_populates="posts")

    @classmethod
    def create(
        cls,
        title,
        content,
        published,
        slug,
        meta_title,
        author,
        category,
        summary=None,
        toc=None,
    ) -> "Post":
        created_at = get_local_datetime(author.timezone)
        published_at = created_at if published else None
        new_post = Post(
            title=title,
            content=content,
            summary=summary,
            toc=toc,
            created_at=created_at,
            updated_at=created_at,
            published=published,
            published_at=published_at,
            slug=slug,
            meta_title=meta_title,
            author=author,
            category=category,
        )
        db.session.add(new_post)
        db.session.commit()
        return Post.query.get(new_post.id)

    def update(
        self,
        title,
        content,
        published,
        slug,
        meta_title,
        author,
        category,
        summary=None,
        toc=None,
    ) -> "Post":
        updated_at = get_local_datetime(author.timezone)
        published_at = updated_at if published else None

        self.title = title
        self.content = content
        self.summary = summary
        self.toc = toc
        self.updated_at = updated_at
        self.published = published
        self.published_at = published_at
        self.slug = slug
        self.meta_title = meta_title
        self.author = author
        self.category = category

        db.session.add(self)
        db.session.commit()

        return Post.query.get(self.id)

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def __repr__(self) -> str:
        return f"<Post {self.title}>"


class Category(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(255))
    content: Mapped[str] = mapped_column(Text, nullable=True)
    slug: Mapped[str] = mapped_column(String(255))
    meta_title: Mapped[str] = mapped_column(String(255))

    posts = relationship("Post", back_populates="category")

    @classmethod
    def create(cls, title, slug, meta_title, content=None) -> "Category":
        new_category = Category(
            title=title,
            slug=slug,
            meta_title=meta_title,
            content=content,
        )
        db.session.add(new_category)
        db.session.commit()

        return Category.query.get(new_category.id)

    def update(self, title, slug, meta_title, content=None) -> "Category":
        self.title = title
        self.slug = slug
        self.meta_title = meta_title
        self.content = content
        db.session.add(self)
        db.session.commit()
        return Category.query.get(self.id)

    def delete(self) -> None:
        default_category = Category.query.first()
        if self is default_category:
            logger.warning(f"Cannot delete default category!!!")
            return None
        for post in self.posts:
            post.category = default_category
            db.session.add(post)
        db.session.commit()
        db.session.delete(self)
        db.session.commit()


class Comment(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    from_owner: Mapped[bool] = mapped_column(Boolean, default=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.today())

    # post = relationship("Post", back_populates="comments")
    # post_id: Mapped[int] = mapped_column(Integer, ForeignKey("post.id"))

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
