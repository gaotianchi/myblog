"""
职责：在写入数据库前以及在验证数据之前将数据处理成指定的格式
"""

import os
from datetime import date

from flask import Flask
from markdown import Markdown

from myblog.model.mdexten import ConvertImgWikiToHtml
from myblog.model.mdexten.customtoc import custom_slugify
from myblog.model.utlis import generate_id, get_meta_and_body


class MetadataProcesser:
    """
    职责：将元数据处理成正确的格式，使元数据可以储存在 MYSQL 数据库中。
    被谁使用：控制器
    使用谁：无
    """

    def __init__(self, app: Flask) -> None:
        self.app = app
        self.__data = {}

    def set(self, md_text: str, path: str) -> None:
        self.meta: dict = get_meta_and_body(md_text)["metadata"]
        self.meta["path"]: str = path.replace("\\", "\\\\")
        self.meta["category"]: str = os.path.basename(os.path.dirname(path))
        self.meta["title"]: str = os.path.basename(path).replace(".md", "")
        self.meta["id"]: str = generate_id(self.meta["title"])
        if not self.meta.get("author", ""):
            self.meta["author"] = "高天驰"

    def __fill_data(self) -> None:
        update: date = date.today()
        post_date: date = self.meta["date"]

        self.__data.update(self.meta)
        self.__data["updated"] = update.strftime("%Y-%m-%d")
        self.__data["date"] = post_date.strftime("%Y-%m-%d")

    @property
    def data(self):
        self.__fill_data()

        return self.__data


class BodyProcesser:
    """
    职责：处理 markdown 文本正文
    被谁使用：控制器
    使用谁：自定义 markdown 拓展模块
    """

    def __init__(self, app: Flask) -> None:
        self.app = app
        self.__data = {"toc": "", "body": ""}
        self.__extension_items = {"extens": [], "config": {}}

    def set(self, md_text: str) -> None:
        self.body = get_meta_and_body(md_text)["body"]

    def __set_extensions(self) -> None:
        """
        职责：配置 markdown 拓展
          - fenced_code: 生成代码块
          - nl2br: 提供非严格 markdown 换行
          - footnotes: 提供引用角标
          - tables: 表格
          - ConvertImgWikiToHtml: 将 ![[imagename]] 转化为 <img src="/image?name=imagename">
          - toc: 生成文章目录
        """
        custom_config = {
            "custom_toc": {
                "title": "文章目录",
                "title_class": "",
                "baselevel": 2,
                "permalink": "#",
                "toc_class": "",
                "slugify": custom_slugify,
            }
        }

        self.__extension_items["extens"] = [
            "fenced_code",
            "nl2br",
            "footnotes",
            "tables",
            "toc",
            ConvertImgWikiToHtml(),
        ]
        self.__extension_items["config"] = {
            "footnotes": {
                "BACKLINK_TEXT": "&#8617;&#xFE0E;",
                "BACKLINK_TITLE": "回到原文被引用的地方",
            },
            "toc": {
                "baselevel": 2,
                "permalink": "#",
                "slugify": custom_slugify,
            },
        }

    def __format_body_to_markdown(self) -> None:
        self.__set_extensions()

        md = Markdown(
            extensions=self.__extension_items["extens"],
            extension_configs=self.__extension_items["config"],
        )

        self.__data["body"]: str = md.convert(self.body)
        self.__data["toc"]: str = md.toc

    @property
    def data(self):
        self.__format_body_to_markdown()

        return self.__data
