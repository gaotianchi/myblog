"""
Abstract: This module defines the database table structure.

Required: myblog.flaskexten.db

Author: Gao Tianchi
Contact: 6159984@gmail.com
Version: 0.3
Creation date: 2023-11-02
Copyright (C) 2023 Gao Tianchi
"""

from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from myblog.flaskexten import db


class PostTable(db.Model):
    __tablename__ = "post"
    id: Mapped[str] = mapped_column(String(20), primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    toc: Mapped[str] = mapped_column(Text, nullable=True)
    release: Mapped[datetime] = mapped_column(DateTime, default=datetime.now())
    updated: Mapped[datetime] = mapped_column(DateTime, default=datetime.now())
    summary: Mapped[str] = mapped_column(Text, nullable=True)

    author_name: Mapped[str] = mapped_column(String(128), ForeignKey("owner.name"))
    category_name: Mapped[str] = mapped_column(String(128), ForeignKey("category.name"))


class CategoryTable(db.Model):
    __tablename__ = "category"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(128), unique=True)

    posts = relationship("PostTable", backref="category")


class OwnerTable(db.Model):
    __tablename__ = "owner"
    name: Mapped[str] = mapped_column(String(128), primary_key=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    email: Mapped[str] = mapped_column(String(128), nullable=True)
    about: Mapped[str] = mapped_column(String(255), nullable=True)
    brith: Mapped[date] = mapped_column(Date, nullable=True)
    country: Mapped[str] = mapped_column(String(128), nullable=True)

    posts = relationship("PostTable", backref="owner")
    site = relationship("SiteTable", backref="owner")


class SiteTable(db.Model):
    __tablename__ = "site"
    blogtitle: Mapped[str] = mapped_column(String(128), primary_key=True)
    blogsubtitle: Mapped[str] = mapped_column(String(128), nullable=True)
    buildingdate: Mapped[date] = mapped_column(Date)
    about: Mapped[str] = mapped_column(String(255), nullable=True)

    owner_name: Mapped[str] = mapped_column(String(128), ForeignKey("owner.name"))
