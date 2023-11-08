import json
import unittest

from myblog import create_app
from myblog.flaskexten import db
from myblog.model.database.db import Category, Owner, Post


class TestOwnerDbHandler(unittest.TestCase):
    def setUp(self) -> None:
        self.app = create_app(environment="testing")
        self.app_context = self.app.app_context()
        self.app_context.push()

        db.session.rollback()
        db.drop_all()
        db.create_all()

    def tearDown(self) -> None:
        self.app_context.pop()

    def test_create_owner_without_name(self):
        new_author = Owner()
        new_author.set_password("hello")

        new_author = Owner.query.filter_by(name="Gao Tianchi").first()

        self.assertIsNotNone(new_author)

        self.assertTrue(new_author.validate_password("hello"))

        db.session.rollback()
        db.drop_all()
        db.create_all()

    def test_create_owner_with_custom_name(self):
        new_author = Owner("gaotianchi")
        new_author.set_password("hello")

        new_author = Owner.query.filter_by(name="gaotianchi").first()
        self.assertIsNotNone(new_author)

        self.assertTrue(new_author.validate_password("hello"))
        db.session.rollback()
        db.drop_all()
        db.create_all()


class TestCategoryDbHandler(unittest.TestCase):
    def setUp(self) -> None:
        self.app = create_app(environment="testing")
        self.app_context = self.app.app_context()
        self.app_context.push()

        db.session.rollback()
        db.drop_all()
        db.create_all()

    def tearDown(self) -> None:
        self.app_context.pop()

    def test_create_without_name(self):
        new_category = Category.create()

        category_name = new_category.name
        default_name = Category.default_name

        self.assertIsNotNone(new_category)
        self.assertEqual(category_name, default_name)

    def test_create_with_a_name(self):
        name = "hello"
        new_category = Category.create(name)

        self.assertIsNotNone(new_category)
        category_name = new_category.name

        self.assertEqual(category_name, name)

    def test_delete_with_default_name(self):
        # Precondition: Method CREATE passed test.
        default_name = Category.default_name
        category = Category.create()

        self.assertIsNotNone(category)

        category.delete()

        name = category.name

        self.assertIsNotNone(category)

        self.assertEqual(default_name, name)


class TestPostDbHandler(unittest.TestCase):
    def setUp(self) -> None:
        self.app = create_app(environment="testing")
        self.app_context = self.app.app_context()
        self.app_context.push()

        db.session.rollback()
        db.drop_all()
        db.create_all()

        author = Owner()
        author.set_password("hello world")

    def tearDown(self) -> None:
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
