import unittest
from datetime import date

from myblog.model.utlis import get_meta_and_body


class TestGetMetaAndBody(unittest.TestCase):
    def test_meta_with_valid_md_text(self):
        md_text = """
---
title: Test Markdown
author: John Doe
date: 2023-10-19
summary: 你好世界！
tags:
  - hello
  - world
---

This is a test markdown document.
"""
        expected_metadata = {
            "title": "Test Markdown",
            "author": "John Doe",
            "date": date(2023, 10, 19),
            "summary": "你好世界！",
            "tags": ["hello", "world"],
        }
        expected_body = "\n\nThis is a test markdown document.\n"
        metadata = get_meta_and_body(md_text)["metadata"]
        body = get_meta_and_body(md_text)["body"]
        self.assertEqual(metadata, expected_metadata)
        self.assertEqual(body, expected_body)

    def test_without_metadata(self):
        md_text = """
        This is a test markdown document without metadata.
        """
        expected_result = {}
        metadata = get_meta_and_body(md_text)["metadata"]
        self.assertEqual(metadata, expected_result)

    def test_with_empty_md_text(self):
        md_text = ""
        expected_result = {}
        metadata = get_meta_and_body(md_text)["metadata"]
        self.assertEqual(metadata, expected_result)
