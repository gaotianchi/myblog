from flask import Flask

from myblog.model.itemloader import TrendLoader


class HomePage:
    """
    职责：提供主页相关数据
    """

    def __init__(self, app: Flask) -> None:
        self.app = app

        self.trendloader = TrendLoader(app)

        self.__data = {}

    def __load_data(self) -> None:
        self.__data = self.trendloader.data

    @property
    def data(self) -> dict:
        self.__load_data()

        return self.__data
