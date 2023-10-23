"""
职责：监视文章工作区的文件变动，返回文件路径和变动类型
被谁使用：
使用谁：
"""
import os
from ast import literal_eval
from datetime import datetime, timedelta

from flask import Flask
from git import Repo


class TrendWatcher:
    def __init__(self, app: Flask) -> None:
        self.app = app

        self.__data = {}

    def __load_trend_data(self) -> None:
        paths: list = os.getenv("PATH_TREND_GIT_REPO").split(",")
        for path in paths:
            commits = self.__get_commits(path)

            self.__data += commits

    def __get_commits(self, path: str) -> list:
        result = []
        repo = Repo(path)
        interval = datetime.now() - timedelta(
            seconds=self.app.config["SCHEDULING_CYCLE_TREND"]
        )
        commits = repo.iter_commits(since=interval)

        for commit in commits:
            message: str = commit.message
            time: datetime = commit.committed_datetime
            hash: str = commit.hexsha[:10]
            author: dict = dict(name=commit.author.name, email=commit.author.email)
            project = os.path.basename(repo.working_dir)

            item = dict(
                hash=hash,
                message=message,
                time=time,
                author=author,
                project=project,
            )

            result.append(item)

        return result

    @property
    def data(self) -> list:
        self.__load_trend_data()

        return self.__data


class PostWatcher:
    """
    职责：获取调度周期内发生变动的文章路径和变动类型。
    被谁使用：文章内容验证器
    """

    def __init__(self, app: Flask) -> None:
        self.app = app
        self.__changed = []

    def __read_commits(self) -> None:
        path_git_userdata = os.getenv("PATH_GIT_USERDATA")
        path_worktree_userdata = os.getenv("PATH_WORKTREE_USERDATA")

        repo = Repo(path_git_userdata)
        interval = datetime.now() - timedelta(
            seconds=self.app.config["SCHEDULING_CYCLE_POST"]
        )
        commits = repo.iter_commits(since=interval)

        changed_files = []

        for commit in commits:
            files = commit.stats.files.keys()
            for f in files:
                filename: str = (
                    literal_eval("b'{f}'".format(f=f)).decode("utf-8").replace('"', "")
                )

                path = os.path.join(path_worktree_userdata, *filename.split("/"))

                if os.path.exists(path):
                    t = "M"
                else:
                    t = "D"

                item = dict(path=path, t=t)

                if not item in changed_files:
                    changed_files.append(item)

        self.__changed = changed_files

    @property
    def data(self) -> list[dict]:
        self.__read_commits()

        if self.__changed:
            self.app.logger.debug(f"下列文章发生变动 {self.__changed}")

        return self.__changed

    def __str__(self) -> str:
        return self.__class__.__name__
