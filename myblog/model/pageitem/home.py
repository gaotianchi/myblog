from flask import Flask

from myblog.model.itemloader import PostLoader, ProfileLoader, TrendLoader


class HomePage:
    """
    职责：提供主页相关数据
    """

    def __init__(self, app: Flask) -> None:
        self.app = app

        self.trendloader = TrendLoader(app)
        self.postloader = PostLoader(app)
        self.profileloader = ProfileLoader(app)

        self.__data = {"recent_trend": [], "profile": {}, "recent_post": []}

    def __load_trends(self) -> None:
        """
        职责：初始化首页的 trend 数据
        """
        self.__data["recent_trend"] = self.trendloader.recent(
            self.app.config["HOME_RECENT_TREND_COUNT"]
        )

    def __load_posts(self) -> None:
        """
        职责：初始化首页的 post 数据
        """
        self.__data["recent_post"] = self.postloader.recent(
            self.app.config["HOME_RECENT_POST_COUNT"]
        )

    def __load_profile(self) -> None:
        """
        职责：初始化首页的 profile 数据
        """
        self.__data["profile"] = self.profileloader.data

    @property
    def data(self) -> dict:
        self.__load_posts()
        self.__load_trends()
        self.__load_profile()

        return self.__data
