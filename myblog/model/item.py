import os
import re
from datetime import datetime, timedelta
from typing import List

import redis
from flask import Flask, url_for
from git.repo import Repo

from myblog.model import pool
from myblog.model.processer import ProfileReader
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
    def author(self) -> str:
        author: bytes = conn.hget(f"post:{self.id}:metadata", "author")

        return author.decode()

    @property
    def body(self) -> str:
        body: bytes = conn.get(f"post:{self.id}:body")

        return body.decode()


class Profile:
    def __init__(self, app: Flask) -> None:
        self.app = app
        self.__reader = ProfileReader(app)

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
    def data(self) -> dict:
        return self.__reader.data["author"]

    def __str__(self) -> str:
        return self.__class__.__name__


class GitLog:
    def __init__(
        self, path: str, since: int = 7, before: int = 0, count: int = 20
    ) -> None:
        self.path = path

        self.__log_to_process = self.__get_log(since, before, count)

    def __get_log(self, s: int, b: int, count: int) -> str:
        repo = Repo(self.path)
        b_date = datetime.now() - timedelta(days=b)
        s_date = datetime.now() - timedelta(days=s)

        git_log: str = repo.git.log(
            '--pretty={"author":"%an","summary":"%s","body":"%b","date":"%cd","hash":"%H"}',
            max_count=count,
            date="format:%Y-%m-%d %H:%M",
            since=s_date.date(),
            before=b_date.date(),
        )

        return git_log

    def __processer_log(self) -> List[dict]:
        data = self.__log_to_process.replace("\n", "")

        pattern = re.compile(
            r'"author":"(.+?)","summary":"(.+?)","body":"(.*?)","date":"(\d{4}-\d{2}-\d{2} \d{2}:\d{2})",\"hash\":\"(.+?)\"',
            re.DOTALL,
        )

        items = re.findall(pattern, data.replace("\n", ""))
        result: List[dict] = []
        if items:
            for i in items:
                remote_repo_name = os.path.basename(self.path)
                # 远程仓库名应与本地仓库名称保持一致

                item = {}
                item["author"] = i[0]
                item["summary"] = i[1]
                item["body"] = i[2]
                item["date"] = i[3]
                item[
                    "commit_link"
                ] = f"https://github.com/2022Jean/{remote_repo_name}/commit/{i[4]}"
                item["author_link"] = "https://github.com/2022Jean"

                result.append(item)

        return result

    @property
    def log(self) -> List[dict]:
        return self.__processer_log()


class Author:
    def __init__(self, app: Flask, **kwargs) -> None:
        self.app = app
        self.kwargs = kwargs

    @property
    def trend(self) -> GitLog:
        count = self.kwargs.get("max_count", 20)
        since = self.kwargs.get("since", 7)
        before = self.kwargs.get("before", 0)

        path = self.kwargs.get("path", self.app.config["GIT_REPO_PATH"])

        return GitLog(path, int(since), int(before), int(count))

    @property
    def profile(self) -> Profile:
        return Profile(self.app)

    @property
    def recent_post(self) -> List[Post]:
        recent_post_count = int(self.kwargs.get("recent_post_count", 5))

        post_ids: List[bytes] = conn.zrange("post:recent", 0, -1)
        self.app.logger.info(post_ids)

        posts: List[Post] = []
        for i in post_ids[0 : recent_post_count - 1]:
            posts.append(Post(self.app, i.decode()))
        self.app.logger.info(posts)

        return posts
