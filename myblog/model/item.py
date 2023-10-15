import os
import re
from datetime import date, datetime, timedelta
from typing import List

import redis
from flask import Flask, url_for
from git.repo import Repo

from myblog.model import pool
from myblog.model.processer import ProfileReader

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
    def data(self) -> dict:
        return self.__reader.data

    def __str__(self) -> str:
        return self.__class__.__name__


class GitLog:
    def __init__(
        self,
        path: str,
        since: str = None,
        before: str = None,
        count: int = 50,
    ) -> None:
        self.path = path

        self.__log_to_process = self.__get_log(since, before, count)

    def __get_log(self, s: str, b: str, count: int) -> str:
        b = datetime.strptime(b, "%Y-%m-%d").date() if b else date.today()

        if not s:
            s = b - timedelta(days=3)
        else:
            s = datetime.strptime(s, "%Y-%m-%d")

        repo = Repo(self.path)

        git_log: str = repo.git.log(
            '--pretty={"author":"%an","summary":"%s","body":"%b","date":"%cd","hash":"%H"}',
            max_count=count,
            date="format:%Y-%m-%d %H:%M",
            since=s,
            before=b,
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
                item["hash"] = i[4]
                item["repo_name"] = remote_repo_name

                result.append(item)

        return result

    @property
    def log(self) -> List[dict]:
        return self.__processer_log()


class Home:
    """
    职责：为首页提供数据
    使用者：首页视图函数
    """

    def __init__(self, app: Flask, **kwargs) -> None:
        self.app = app
        self.kwargs = kwargs

    @property
    def trend(self) -> List[dict]:
        before = str(date.today())
        since = str(date.today() - timedelta(days=7))

        count = int(self.kwargs.get("count", 20))

        since = self.kwargs.get("since", "")
        before = self.kwargs.get("before", "")

        paths: list = self.profile.data["gitrepo"]

        timeline = LogTimeLine(
            self.app, paths=paths, since=since, before=before, count=count
        )

        return timeline.logs

    @property
    def profile(self) -> Profile:
        return Profile(self.app)

    @property
    def recent_post(self) -> List[Post]:
        recent_post_count = int(self.kwargs.get("recent_post_count", 5))

        post_ids: List[bytes] = conn.zrange("post:recent", 0, -1, desc=True)

        posts: List[Post] = []
        for i in post_ids[0 : recent_post_count - 1]:
            posts.append(Post(self.app, i.decode()))

        return posts


class LogTimeLine:
    """
    职责：将多个仓库的日志按照时间排序，返回一个列表
    使用者: item.Home
    组件:
        1. item.GitLog
        2. item.Profile
    """

    def __init__(self, app: Flask, paths: list, **kwargs) -> None:
        self.app = app
        self.paths = paths
        self.kwargs = kwargs

    def __sort_logs(self) -> list:
        count = int(self.kwargs.get("count", 50))

        since = self.kwargs.get("since", "")

        before = self.kwargs.get("before", "")

        paths = self.paths
        self.app.logger.info(f"{self} 接收到的 before 值为 {before}")
        self.app.logger.info(f"{self} 接收到的 since 值为 {since}")

        result = []
        for p in paths:
            loghandler = GitLog(p, since, before, count)
            logs = loghandler.log
            self.app.logger.debug(f"{self} 从 {p} 中获取到 {len(logs)} 个日志")
            result += logs

        result = sorted(result, key=lambda x: x["date"], reverse=True)
        self.app.logger.info(f"{self} 获取到的 git 日志包括 {result}")

        return result

    @property
    def logs(self) -> list:
        return self.__sort_logs()

    def __str__(self) -> str:
        return self.__class__.__name__
