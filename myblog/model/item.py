import os

import redis
from flask import Flask

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
