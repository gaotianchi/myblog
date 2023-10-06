import os

import redis
from flask import Flask, url_for

from myblog.model import pool
from myblog.model.processer import WritingSpaceReader
from myblog.utlis import generate_id

conn = redis.Redis(connection_pool=pool)


class WritingSpace:
    def __init__(self, app: Flask) -> None:
        self.app = app
        self.__reader = WritingSpaceReader(app)

    @property
    def home_post_title(self) -> str:
        temp = str(self.__reader.data["path"]["homePostPath"]).split("/")
        home_post_path = os.path.join(self.app.config["DATA_DIR"], *temp)
        self.app.logger.debug(f"{self} 检测到 home_post_path: {home_post_path}")

        if not (os.path.exists(home_post_path) and home_post_path.endswith(".md")):
            self.app.logger.debug(f"{self} 没有找到指定的主页文章路径，开始尝试在数据库中寻找最新的文章作为主页文章。")
            latest_post = conn.zrange("post:recent", -1, -1)
            if latest_post:
                latest_post_id = latest_post[0].decode()
                post_title = conn.hget(
                    f"post:{latest_post_id}:metadata", "title"
                ).decode()

                self.app.logger.debug(f"{self} 在数据库中将最新的文章 {post_title} 作为首页文章。")

                return latest_post_id
            else:
                self.app.logger.warn(f"{self} 没有找到任何文章作为首页文章！")
                return None
        else:
            title = os.path.basename(home_post_path).replace(".md", "").replace(" ", "")
            return generate_id(title)

    @property
    def author(self) -> dict:
        return self.__reader.data["author"]

    def __str__(self) -> str:
        return self.__class__.__name__


class Article:
    def __init__(self, app: Flask, title: str) -> None:
        self.app = app
        self.title = title

    @property
    def date(self) -> str:
        date = conn.hget(f"post:{self.title}:metadata", "date")

        return date.decode()

    @property
    def body(self) -> str:
        body = conn.get(f"post:{self.title}:body")

        return body.decode()

    @property
    def url(self) -> str:
        return url_for("api.article", title=self.title)

    def __get_recent_article(self) -> list:
        temp_recent = conn.zrange("post:recent", 0, -1)
        recent = [title.decode() for title in temp_recent]

        return recent if recent else []

    @property
    def older(self):
        recent_list = self.__get_recent_article()

        if not recent_list:
            return None

        if recent_list.index(self.title) == 0:
            return None

        older_title = recent_list[recent_list.index(self.title) - 1]

        return Article(self.app, older_title)

    @property
    def newer(self):
        recent_list = self.__get_recent_article()

        if not recent_list:
            return None

        if recent_list.index(self.title) == len(recent_list) - 1:
            return None

        newer_title = recent_list[recent_list.index(self.title) + 1]

        return Article(self.app, newer_title)

    def __str__(self) -> str:
        return self.__class__.__name__
