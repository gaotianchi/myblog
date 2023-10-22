"""
职责：拓展文章目录功能
"""

import re
from xml.etree import ElementTree

from markdown.extensions.toc import TocExtension, TocTreeprocessor


def custom_slugify(value, separator):
    """自定义锚点链接"""

    value = re.sub(r"[^\w\s-]", "", value).strip().lower()
    return re.sub(r"[{}\s]+".format(separator), separator, value)


class CustomTocprocesser(TocTreeprocessor):
    """
    职责：自定义目录的节点结构
    2023-10-22 暂时不需要
    """

    def __init__(self, md, config) -> None:
        super().__init__(md, config)

    def build_toc_div(self, toc_list):
        div = ElementTree.Element("div")
        div.attrib["class"] = self.toc_class

        if self.title:
            header = ElementTree.SubElement(div, "h4")
            if self.title_class:
                header.attrib["class"] = self.title_class
            header.text = self.title

        def build_etree_ul(toc_list, parent):
            ul = ElementTree.SubElement(parent, "ul")
            for item in toc_list:
                li = ElementTree.SubElement(ul, "li")
                link = ElementTree.SubElement(li, "a")
                link.text = item.get("name", "")
                link.attrib["href"] = "#" + item.get("id", "")
                if item["children"]:
                    build_etree_ul(item["children"], li)
            return ul

        build_etree_ul(toc_list, div)

        if "prettify" in self.md.treeprocessors:
            self.md.treeprocessors["prettify"].run(div)

        return div


class CustomTocExtension(TocExtension):
    """
    职责：注册自定义的拓展
    """

    TreeProcessorClass = CustomTocprocesser

    def extendMarkdown(self, md):
        """Add TOC tree processor to Markdown."""
        md.registerExtension(self)
        self.md = md
        self.reset()
        tocext = self.TreeProcessorClass(md, self.getConfigs())
        md.treeprocessors.register(tocext, "custom_toc", 1)


def makeExtension(**kwargs):
    return CustomTocExtension(**kwargs)
