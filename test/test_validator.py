import profile
import unittest
from datetime import datetime

from flask import Flask

from myblog.model.utlis import get_data_from_json_file
from myblog.model.validator import ProfileValidator, ValidatorFactory
from myblog.setting import config


class TrendValidatorTestCase(unittest.TestCase):
    def setUp(self) -> None:
        app = Flask(__name__)
        app.config.from_object(config["base"])

        validator_factory = ValidatorFactory(app)
        self.validator = validator_factory.get_validator("trend")

        self.valid_commit_items: dict = {
            "message": "\n这是消息的摘要部分\n\n接下来是消息的正文部分，正文部分的最小字数为10个字。\n最大字数为1000个字。#publish",
            "time": datetime.today(),
            "author": {"name": "高天驰", "email": "6159984@gmail.com"},
            "project": "myblog",
        }

        self.invalid_commit_items: dict = {
            "message": "字太少\n字太少",
            "time": datetime.today(),
            "author": {"name": "", "email": ""},
            "project": "myblog",
        }

    def test_valid_commit_items(self):
        self.validator.set(self.valid_commit_items)
        self.assertTrue(self.validator.validate())

    def test_invalid_commit_items(self):
        self.validator.set(self.invalid_commit_items)
        self.assertFalse(self.validator.validate())

    def test_validate_datetime(self):
        self.validator.set(self.valid_commit_items)
        self.assertTrue(self.validator._TrendValidator__validate_datetime())

    def test_validate_word_count(self):
        self.validator.set(self.valid_commit_items)
        self.assertTrue(self.validator._TrendValidator__validate_word_count())
        self.validator.set(self.invalid_commit_items)
        self.assertFalse(self.validator._TrendValidator__validate_word_count())

    def test_validate_whether_to_publish(self):
        self.validator.set(self.valid_commit_items)
        self.assertTrue(self.validator._TrendValidator__validate_whether_to_publish())
        self.validator.set(self.invalid_commit_items)
        self.assertFalse(self.validator._TrendValidator__validate_whether_to_publish())


class ProfileValidatorTestCase(unittest.TestCase):
    def setUp(self) -> None:
        app = Flask(__name__)
        app.config.from_object(config["base"])
        self.validator = ProfileValidator(app)

    def test_valid_profile(self):
        path = "D:\\dev\\repo\\myblog\\test\\example_file\\profile.json"
        profile = get_data_from_json_file(path)
        self.validator.set(profile)

        self.assertTrue(self.validator._ProfileValidator__validate_trend_repo())
        self.assertTrue(self.validator._ProfileValidator__validate_author())
        self.assertTrue(self.validator._ProfileValidator__validate_website())
