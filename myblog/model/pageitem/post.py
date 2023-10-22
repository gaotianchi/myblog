"""
职责：为 post.html 页面模板提供所需数据
"""

from ast import Dict

from flask import Flask

from myblog.model.itemloader import PostLoader


class PostPage:
    """
    职责：提供文章页面相关数据
    """

    def __init__(self, app: Flask) -> None:
        self.app = app

        self.postloader = PostLoader(app)

        self.__data = {}

    def set(self, post_id: str) -> None:
        self.postloader.set(post_id)

    def __load_data(self) -> None:
        self.__data = self.postloader.data

    @property
    def data(self) -> Dict:
        self.__load_data()

        return self.__data
