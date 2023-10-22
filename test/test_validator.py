import unittest
from datetime import date

from flask import Flask

from myblog.model.validator import PostBodyValidator, PostMetadataValidator


class PostMetadataValidatorTest(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.validator = PostMetadataValidator(self.app)
        self.app.config["REQUIRED_POST_KEY"] = {
            "date": date,
            "summary": str,
            "tags": list,
        }

    def test_valid_meta(self):
        self.validator.meta = {
            "date": date(2023, 10, 19),
            "summary": "hello world",
            "tags": ["hello", "world"],
        }
        self.assertTrue(self.validator.valid)

    def test_invalid_type(self):
        self.validator.meta = {
            "date": date(2023, 10, 19),
            "summary": "hello world",
            "tags": '["hello", "world"]',
        }
        self.assertFalse(self.validator.valid)

    def test_messing_key(self):
        self.validator.meta = {
            "date": date(2023, 10, 19),
            "summary": "hello world",
        }
        self.assertFalse(self.validator.valid)


class PostBodyValidatorTest(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.validator = PostBodyValidator(self.app)

    def test_body_without_table(self):
        self.validator.body = """
hello world
"""
        result = self.validator.valid
        self.assertFalse(result)

    def test_valid_body(self):
        self.validator.body = """
# hello
## world
hello world
"""
        result = self.validator.valid
        self.assertTrue(result)
