import json
import os
import unittest
from pathlib import Path

from myblog import create_app
from myblog.flaskexten import db
from myblog.help import encrypt_token
from myblog.model.database.db import Owner, Post

ownerspace = Path(__file__).parent.joinpath("ownerspace")


class TestOwnerController(unittest.TestCase):
    # Precondition: The database operation handle passes the test
    def setUp(self) -> None:
        self.app = create_app(environment="testing")
        self.app_context = self.app.app_context()
        self.app_context.push()

        db.session.rollback()
        db.drop_all()

        db.create_all()

        author = Owner()
        author.set_password("hello world")

        self.client = self.app.test_client()

        with open(self.app.config["PATH_KEY"], "r", encoding="utf-8") as f:
            key = f.read().encode("utf-8")

        self.token = encrypt_token(key, json.dumps(dict(name=author.name)))

    def tearDown(self) -> None:
        self.app_context.pop()

    # def test_add_post_without_token(self):
    #     new_post_path = ownerspace.joinpath(*["post", "add_post.md"])

    #     json_data: str = json.dumps(dict(path=str(new_post_path)))

    #     response = self.client.post(
    #         "/add/post",
    #         json=json_data,
    #     )

    #     self.assertIn("<title>401 Unauthorized</title>", response.text)

    def test_add_post_with_valid_token(self):
        new_post_path = ownerspace.joinpath(*["post", "post_with_metadata_and_toc.md"])

        json_data: str = json.dumps(dict(path=str(new_post_path)))

        response = self.client.post(
            f"/add/post?token={self.token}",
            json=json_data,
        )

        self.assertEqual(response.status_code, 200)

        post = Post.query.filter_by(title="post_with_metadata_and_toc").first()
        self.assertIsNotNone(post)
        category_name: str = post.category_name

        self.assertEqual(category_name, "uncategorized")

    def test_update_post(self):
        # Precondition: The view function add_function passes the test.

        new_post_path = ownerspace.joinpath(*["post", "post_with_metadata_and_toc.md"])

        json_data: str = json.dumps(dict(path=str(new_post_path)))

        self.client.post(
            f"/add/post?token={self.token}",
            json=json_data,
        )

        response_2 = self.client.patch(
            f"/update/post?token={self.token}",
            json=json_data,
        )

        self.assertEqual(response_2.status_code, 200)

    def test_delete_post(self):
        # Precondition: The view function add_function passes the test.

        new_post_path = ownerspace.joinpath(*["post", "post_to_delete.md"])

        with open(new_post_path, "w") as f:
            f.write("hello world")

        json_data: str = json.dumps(dict(path=str(new_post_path)))

        self.client.post(
            f"/add/post?token={self.token}",
            json=json_data,
        )

        new_post = Post.query.filter_by(title="post_to_delete").first()

        self.assertIsNotNone(new_post)

        self.client.delete(
            f"/delete/post?token={self.token}",
            json=json_data,
        )

        post = Post.query.filter_by(title="post_to_delete").first()

        self.assertIsNone(post)


class TestVisitorController(unittest.TestCase):
    # Precondition: Owner Controller passes the test.
    def setUp(self) -> None:
        self.app = create_app(environment="testing")
        self.app_context = self.app.app_context()
        self.app_context.push()

        db.session.rollback()
        db.drop_all()

        db.create_all()

        author = Owner()
        author.set_password("hello world")

        self.client = self.app.test_client()

    def tearDown(self) -> None:
        self.app_context.pop()

    def test_read_post(self):
        new_post_path = ownerspace.joinpath(*["post", "post_with_metadata_and_toc.md"])

        json_data: str = json.dumps(dict(path=str(new_post_path)))

        response = self.client.post(
            f"/add/post",
            json=json_data,
        )

        self.assertEqual(response.status_code, 200)

        post = Post.query.filter_by(title="post_with_metadata_and_toc").first()

        self.assertIsNotNone(post)

        post_id = post.id

        self.assertIsNotNone(post_id)

        response = self.client.get(f"/read/post?id={post_id}")

        self.assertEqual(response.status_code, 200)

        self.assertIn("post_with_metadata_and_toc", response.text)
