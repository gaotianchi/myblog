"""
Abstract: This module defines the rendering method for specific data types.

Author: Gao Tianchi
Contact: 6159984@gmail.com
Version: 0.3
Creation date: 2023-11-05
Copyright (C) 2023 Gao Tianchi
"""

from pathlib import Path

from myblog.help import get_post_items

from .render import Render


class PostRender:
    def __init__(self) -> None:
        self.render = Render()
        self.__data = {
            "body": "",
            "toc": None,
            "summary": None,
            "title": "",
            "category": "",
        }

    def set(self, path: str, **kwargs) -> None:
        self.path = Path(path)
        self.kwargs = kwargs

        with open(path, "r", encoding="utf-8") as f:
            content = f.read()

        self.metadata: dict = get_post_items(content)["metadata"]
        self.md_body: str = get_post_items(content)["body"]
        summary_length: int = self.kwargs.get("summary_length", 200)
        self.md_summary: str = self.md_body[:summary_length]

    def __prcess_items(self) -> None:
        self.__data["title"] = self.path.stem
        self.__data["body"] = self.render(self.md_body)
        self.__data["toc"] = self.render.toc
        self.__data["summary"] = self.render(self.md_summary)
        postdirname: str = self.kwargs.get("postdir", "post")
        self.__data["category"] = (
            None if self.path.parent.stem == postdirname else self.path.parent.stem
        )

    @property
    def data(self) -> dict:
        self.__prcess_items()
        return self.__data
