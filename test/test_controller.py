import json
import os
import unittest

from myblog import create_app
from myblog.flaskexten import db
from myblog.model.database.db import Owner


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

    def test_add_post_without_token(self):
        new_post_path: str = os.path.join(
            self.app.config["PATH_OWNER_WORK_REPO"],
            *["post", "add_post.md"],
        )

        response = self.client.post(
            "/add/post",
            json=dict(path=new_post_path),
        )

        self.assertIn("<title>401 Unauthorized</title>", response.text)
