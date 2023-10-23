import re
import unittest
from datetime import datetime

from flask import Flask

from myblog.model.processer import TrendProcesser
from myblog.setting import config


class TrendProcesserTestCase(unittest.TestCase):
    def setUp(self) -> None:
        app = Flask(__name__)
        app.config.from_object(config["base"])

        self.processer = TrendProcesser(app)

        self.commit_items: dict = {
            "message": "\n这是消息的摘要部分\n\n接下来是消息的正文部分，正文部分的最小字数为10个字。\n最大字数为1000个字。#publish",
            "time": datetime.today(),
            "hash": "hsdfksldfjls",
            "project": "myblog",
            "author": {"name": "高天驰", "email": "615984@gmail.com"},
        }

    def test_data(self):
        self.processer.set(self.commit_items)
        result = self.processer.data

        self.assertEqual(result["title"], "这是消息的摘要部分")
        self.assertEqual(
            result["body"], "<p>接下来是消息的正文部分，正文部分的最小字数为10个字。\n最大字数为1000个字。</p>"
        )
        matches = re.match(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}", result["time"])
        self.assertTrue(matches)
