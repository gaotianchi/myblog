import json
import unittest

from myblog import create_app
from myblog.flaskexten import db
from myblog.model.database.db import Category, Owner, Post


class TestPostDbHandler(unittest.TestCase):
    def setUp(self) -> None:
        self.app = create_app(environment="testing")
        self.app_context = self.app.app_context()
        self.app_context.push()

        db.session.rollback()

        db.create_all()

        author = Owner()
        author.set_password("hello world")

    def tearDown(self) -> None:
        db.session.rollback()
        db.drop_all()
        self.app_context.pop()

    def test_create_post_without_category(self):
        # Precondition: Category operation class passes the test.
        data = dict(
            title="hello world",
            body="hello world",
        )
        try:
            new_post = Post.create(data)
        except:
            db.session.rollback()

        self.assertIsNotNone(new_post)

        title = new_post.title
        body = new_post.body
        category_name = new_post.category_name

        self.assertEqual(title, "hello world")
        self.assertEqual(body, "hello world")
        self.assertEqual(category_name, "uncategorized")

    def test_create_post_with_category(self):
        # Precondition: Category operation class passes the test.
        data = dict(
            title="hello world",
            body="hello world",
            category="new category",
        )
        try:
            new_post = Post.create(data)
            new_category = Category.query.filter_by(name=data["category"]).first()
        except:
            db.session.rollback()

        self.assertIsNotNone(new_post)
        self.assertIsNotNone(new_category)

        title = new_post.title
        body = new_post.body
        category_name = new_post.category_name

        self.assertEqual(title, "hello world")
        self.assertEqual(body, "hello world")
        self.assertEqual(category_name, data["category"])

    def test_delete(self):
        # Precondition:
        #     1. Category operation class passes the test.
        #     2. classmethod Post.create passes the test.

        data = dict(
            title="test delete",
            body="test delete",
        )

        try:
            new_post = Post.create(data)
            new_post.delete()
        except:
            db.session.rollback()

        post = Post.query.filter_by(title=data["title"]).first()
        self.assertIsNone(post)

    def test_to_json(self):
        # Precondition:
        #     1. Category operation class passes the test.
        #     2. classmethod Post.create passes the test.
        data = dict(
            title="test delete",
            body="test delete",
        )

        try:
            new_post = Post.create(data)
            actual_json_data: str = new_post.to_json()
        except:
            db.session.rollback()

        self.assertIsNotNone(actual_json_data)
        actual_dict_data = json.loads(actual_json_data)

        self.assertEqual(actual_dict_data["title"], data["title"])
        self.assertEqual(actual_dict_data["body"], data["body"])
        self.assertEqual(actual_dict_data["category"], "uncategorized")
