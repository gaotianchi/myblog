"""
Abstract: This module defines the database table structure.

Required: myblog.flaskexten.db

Author: Gao Tianchi
Contact: 6159984@gmail.com
Version: 0.3
Creation date: 2023-11-02
Latest modified date: 2023-11-02
Copyright (C) 2023 Gao Tianchi
"""

from datetime import date

from sqlalchemy import Date, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from myblog.flaskexten import db


class PostTable(db.Model):
    __tablename__ = "post"
    id: Mapped[str] = mapped_column(String(20), primary_key=True)
    title: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    toc: Mapped[str] = mapped_column(Text, nullable=False)
    author: Mapped[str] = mapped_column(String(50), nullable=False)
    release: Mapped[date] = mapped_column(Date, default=date.today())
    updated: Mapped[date] = mapped_column(Date, default=date.today())
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str] = mapped_column(String(30), nullable=False)


class OwnerTable(db.Model):
    __tablename__ = "owner"
    name: Mapped[str] = mapped_column(String(128), primary_key=True)
    password_hash: Mapped[str] = mapped_column(String(128))
    email: Mapped[str] = mapped_column(String(128))
    about: Mapped[str] = mapped_column(String(255))
    brith: Mapped[date] = mapped_column(Date)
    country: Mapped[str] = mapped_column(String(128))
