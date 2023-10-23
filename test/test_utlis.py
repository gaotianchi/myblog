import unittest

from myblog.model.utlis import get_summary_and_body


class TestGetSummaryBody(unittest.TestCase):
    def test_valid_git_message(self):
        message: str = """
这里是消息的摘要信息

这里是消息的主体这里是消息的主体
这里是消息的主体

"""
        items = get_summary_and_body(message)

        self.assertEqual(items["summary"], "这里是消息的摘要信息")
        self.assertEqual(items["body"], "这里是消息的主体这里是消息的主体\n这里是消息的主体")

    def test_empty_git_message(self):
        message: str = ""

        items = get_summary_and_body(message)

        self.assertEqual(items["summary"], "")
        self.assertEqual(items["body"], "")
