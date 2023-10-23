"""
职责：定时运行指定任务
"""


import os

from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask

from myblog.model.controller import PostUpdater, TrendUpdater
from myblog.model.watcher import PostWatcher, TrendWatcher


class PostTask:
    """
    职责：定义更新文章的任务
    被谁使用：计时器
    使用谁：
      - 文章监视器
      - 文章更新器
    """

    def __init__(self, app: Flask) -> None:
        self.app = app

        self.watcher = PostWatcher(app)
        self.updater = PostUpdater(app)

    def __update(self):
        items: list[dict] = self.watcher.data

        for item in items:
            path: str = item["path"]
            t: str = item["t"]
            self.updater.set(path, t)
            self.updater.update()

    def update_post(self):
        self.__update()

    def __str__(self) -> str:
        return self.__class__.__name__


class TrendTask:
    """
    职责：定义更新动态内容的任务
    被谁使用：计时器
    """

    def __init__(self, app: Flask) -> None:
        self.app = app

        self.watcher = TrendWatcher(app)
        self.updater = TrendUpdater(app)

    def update_trend(self) -> None:
        paths: list[str] = os.getenv("PATH_TREND_GIT_REPO").split(",")

        if not paths:
            self.app.logger.warn("没有设置 git 仓库，无法获取动态内容")
            return None

        commits_items: list[dict] = self.watcher.data
        for items in commits_items:
            self.updater.set(items)

            self.updater.update()


class Scheduler:
    """
    职责：注册任务，定时执行任务
    被谁使用：应用后台
    使用谁：
      - 文章定时器
    """

    def __init__(self, app: Flask) -> None:
        self.app = app
        self.scheduler = BackgroundScheduler()
        self.post_task = PostTask(app)
        self.trend_task = TrendTask(app)

    def job_update_post(self) -> None:
        PATH_GIT_USERDATA = os.getenv("PATH_GIT_USERDATA")
        PATH_WORKTREE_USERDATA = os.getenv("PATH_WORKTREE_USERDATA")

        if not PATH_GIT_USERDATA or not PATH_WORKTREE_USERDATA:
            return None

        self.post_task.update_post()

    def job_update_trend(self) -> None:
        self.trend_task.update_trend()

    def run(self):
        self.app.logger.info("启动定时任务")

        self.scheduler.add_job(
            func=self.job_update_post,
            trigger="interval",
            seconds=self.app.config["SCHEDULING_CYCLE_POST"],
        )

        self.scheduler.add_job(
            func=self.job_update_trend,
            trigger="interval",
            seconds=self.app.config["SCHEDULING_CYCLE_TREND"],
        )

        self.scheduler.start()

    def __str__(self) -> str:
        return self.__class__.__name__
