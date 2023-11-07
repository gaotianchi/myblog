import unittest
from pathlib import Path

from myblog.help import get_post_items

resources = Path(__file__).parent / "ownerspace"


class TestHelp(unittest.TestCase):
    def test_get_post_items_with_empty_post(self):
        md_text: str = ""

        data = get_post_items(md_text)

        self.assertEqual(data["metadata"], {})
        self.assertEqual(data["body"], "")

    def test_get_post_items_with_metadata(self):
        filepath = resources.joinpath("post", "post_with_metadata.md")

        with open(filepath, "r", encoding="utf-8") as f:
            md_text = f.read()

        metadata: dict = get_post_items(md_text)["metadata"]
        body: str = get_post_items(md_text)["body"]

        self.assertEqual(metadata, {"category": "hello"})
        self.assertEqual(body.strip(), "hello world")
