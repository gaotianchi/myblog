import unittest

from myblog.model.mdrender.render import PostRender


class TestPostRender(unittest.TestCase):
    def setUp(self) -> None:
        self.render = PostRender()

    def test_text_with_toc(self):
        md_text_with_toc = """
# Lorem, ipsum dolor.
## Lorem, ipsum dolor.
"""

        self.render(md_text_with_toc)

        toc = self.render.toc.strip()

        expect_toc = """
<div class="toc">
<ul>
<li><a href="#lorem-ipsum-dolor">Lorem, ipsum dolor.</a><ul>
<li><a href="#lorem-ipsum-dolor_1">Lorem, ipsum dolor.</a></li>
</ul>
</li>
</ul>
</div>
""".strip()
        self.assertEqual(toc, expect_toc)

    def test_text_without_toc(self):
        md_text_without_toc = """
Lorem, ipsum dolor.
Lorem, ipsum dolor.
"""
        self.render(md_text_without_toc)

        toc = self.render.toc

        self.assertIsNone(toc)
