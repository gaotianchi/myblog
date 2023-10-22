import unittest
from xml.etree import ElementTree

from markdown import Markdown

from myblog.model.mdexten import ConvertImgWikiToHtml, CustomTocExtension


class ImageExtensionTest(unittest.TestCase):
    def test_image_extension(self):
        md = Markdown(extensions=[ConvertImgWikiToHtml()])
        html = md.convert("Hello, World! ![[imagename]]")
        expected_html = '<p>Hello, World! <img src="/image?name=imagename" /></p>'
        self.assertEqual(html, expected_html)

    def test_CustomTocExtension_without_table(self):
        md = Markdown(extensions=[CustomTocExtension()])
        text = """你好世界！"""
        md.convert(text)
        table = md.toc
        expected_html = '<div class="toc">\n<ul></ul>\n</div>\n'
        self.assertEqual(table, expected_html)
