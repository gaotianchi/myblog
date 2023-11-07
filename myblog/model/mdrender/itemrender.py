"""
Abstract: This module defines the rendering method for specific data types.

Author: Gao Tianchi
Contact: 6159984@gmail.com
Version: 0.3
Creation date: 2023-11-05
Copyright (C) 2023 Gao Tianchi
"""

from myblog.help import get_post_items

from .render import Render


class PostRender:
    def __init__(self) -> None:
        self.render = Render()
        self.__data = {
            "body": "",
            "toc": "",
        }

    def set(self, path: str) -> None:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()

        items: dict = get_post_items(content)

        self.body: dict = items["body"]

    def __render_post(self) -> None:
        body = self.render(self.body)
        toc = self.render.toc

        self.__data["body"] = body
        self.__data["toc"] = toc

    @property
    def data(self) -> dict:
        self.__render_post()

        return self.__data
