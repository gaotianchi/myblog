import unittest

from myblog import create_app
from myblog.flaskexten import db
from myblog.model.database.db import Category, Owner, Post


class TestPostDbHandler(unittest.TestCase):
    # Precondition: The database operation handle passes the test
    def setUp(self) -> None:
        self.app = create_app(environment="testing")
        self.app_context = self.app.app_context()
        self.app_context.push()

        db.session.rollback()

        db.create_all()

        author = Owner()
        author.set_password("hello world")

        self.client = self.app.test_client()

    def tearDown(self) -> None:
        db.session.rollback()
        db.drop_all()
        self.app_context.pop()

    def test_add_post(self):
        ...
