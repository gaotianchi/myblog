"""
Created: 2023-11-25
Author: Gao Tianchi
"""


from datetime import datetime
from random import randint

from faker import Faker

from .flaskexten import db
from .model.database import Category, Comment, Post

fake = Faker()


def fake_categories(count: int = 5):
    Category.create("Uncategorized")
    for _ in range(count):
        Category.create(title=fake.word())


def fake_posts(count: int = 50):
    for _ in range(count):
        title: str = fake.sentence(nb_words=6, variable_nb_words=True)[:-1]
        paragraphs: str = [
            "<p>" + fake.paragraph(nb_sentences=10) + "</p>" for _ in range(15)
        ]
        category = Category.query.get(randint(1, Category.query.count()))
        start_date = datetime(2021, 1, 1, 1, 1, 1)
        post = Post(
            title=title,
            body="".join(paragraphs),
            author=fake.name(),
            category=category,
            summary=fake.paragraph(nb_sentences=7),
            created=fake.date_time_between(start_date=start_date),
        )

        db.session.add(post)
    db.session.commit()


def fake_comments(count: int = 100):
    for _ in range(count):
        comment = Comment(
            content=fake.sentence(),
            timestamp=fake.date_time_this_year(),
            post=Post.query.get(randint(1, Post.query.count())),
        )
        db.session.add(comment)

    db.session.commit()

    for _ in range(count):
        reply_to = Comment.query.get(randint(1, Comment.query.count()))
        post = reply_to.post
        comment = Comment(
            content=fake.sentence(),
            timestamp=fake.date_time_this_year(),
            reply_to=reply_to,
            post=post,
        )
        db.session.add(comment)
    db.session.commit()
