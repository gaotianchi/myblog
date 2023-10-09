import os
from typing import List

import redis
from flask import Flask, url_for

from myblog.model import pool
from myblog.model.processer import WritingSpaceReader
from myblog.utlis import generate_id

conn = redis.Redis(connection_pool=pool)


class Post:
    def __init__(self, app: Flask, id: str) -> None:
        self.app = app
        self.id = id

    def __get_post_metadata(self) -> dict:
        name = f"post:{self.id}:metadata"
        metadata = {}
        keys = conn.hgetall(name)

        for key in keys:
            value = conn.hget(name, key)

            key: bytes
            value: bytes

            if key == b"tags":
                metadata[key.decode()] = eval(value.decode())
            else:
                metadata[key.decode()] = value.decode()

        return metadata

    def __get_recent_posts(self) -> List:
        """从旧到新的排列方式"""

        recent: List[bytes] = conn.zrange("post:recent", 0, -1)

        return [post.decode() for post in recent]

    @property
    def older(self) -> "Post":
        recent: List[str] = self.__get_recent_posts()

        self_index: int = recent.index(self.id)

        if self_index == 0:
            return None

        return Post(self.app, recent[self_index - 1])

    @property
    def newer(self) -> "Post":
        recent: List[str] = self.__get_recent_posts()

        self_index: int = recent.index(self.id)

        if self_index == len(recent) - 1:
            return None

        return Post(self.app, recent[self_index + 1])

    @property
    def metadata(self) -> dict:
        return self.__get_post_metadata()

    @property
    def table(self) -> str:
        t: bytes = conn.get(f"post:{self.id}:table")

        return t.decode()

    @property
    def url(self) -> str:
        with self.app.app_context():
            url = url_for("user.read_post", id=self.id)

        return url

    @property
    def title(self) -> str:
        title: bytes = conn.hget(f"post:{self.id}:metadata", "title")

        return title.decode()

    @property
    def category(self) -> str:
        category: bytes = conn.hget(f"post:{self.id}:metadata", "category")

        return category.decode()

    @property
    def tags(self) -> List:
        tags: bytes = conn.hget(f"post:{self.id}:metadata", "tags")

        return eval(tags)

    @property
    def date(self) -> str:
        date: bytes = conn.hget(f"post:{self.id}:metadata", "date")

        return date.decode()

    @property
    def summary(self) -> str:
        summary: bytes = conn.hget(f"post:{self.id}:metadata", "summary")

        return summary.decode()

    @property
    def updated(self) -> str:
        updated_time: bytes = conn.hget(f"post:{self.id}:metadata", "updated")

        return updated_time.decode()

    @property
    def body(self) -> str:
        body: bytes = conn.get(f"post:{self.id}:body")

        return body.decode()


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
