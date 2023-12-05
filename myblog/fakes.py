"""
Created: 2023-11-25
Author: Gao Tianchi
"""


import random

from faker import Faker

from .flaskexten import db
from .model.database import Category, Comment, Post, User

fake = Faker()


def fake_user():
    user_profile = fake.profile()
    new_user = User.create(
        name=user_profile["name"],
        email=user_profile["mail"],
        password="admin",
        intro=fake.sentence(nb_words=30),
        timezone="Asia/Shanghai",
        profile=fake.paragraph(nb_sentences=10),
    )
    return new_user


def fake_categories(count: int = 2):
    default_category = Category.create(
        "Uncategorized", slug="Uncategorized", meta_title="Uncategorized"
    )
    categories = [default_category]
    for _ in range(count):
        title = fake.word()
        c = Category.create(title=title, slug=title, meta_title=title)
        categories.append(c)
    return categories


def fake_posts(count: int = 10):
    posts = []
    for _ in range(count):
        title: str = fake.sentence(nb_words=6, variable_nb_words=True)[:-1]
        content = ""
        for i in range(15):
            paragraph = "<p>" + fake.paragraph(nb_sentences=15) + "</p>"
            content += paragraph

        published = random.choice([False, True])
        slug = title.lower().replace(" ", "-")
        meta_title = title
        author = User.query.first()
        category = Category.query.get(random.randint(1, Category.query.count()))
        new_post = Post.create(
            title, content, published, slug, meta_title, author, category
        )
        posts.append(new_post)

    return posts


def fake_comments(count: int = 100):
    for _ in range(count):
        comment = Comment(
            content=fake.sentence(),
            timestamp=fake.date_time_this_year(),
            post=Post.query.get(random.randint(1, Post.query.count())),
        )
        db.session.add(comment)

    db.session.commit()

    for _ in range(count):
        reply_to = Comment.query.get(random.randint(1, Comment.query.count()))
        post = reply_to.post
        comment = Comment(
            content=fake.sentence(),
            timestamp=fake.date_time_this_year(),
            reply_to=reply_to,
            post=post,
        )
        db.session.add(comment)
    db.session.commit()
