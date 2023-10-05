from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask
from watchdog.events import PatternMatchingEventHandler
from watchdog.observers import Observer

from myblog.model.processer import PostCleaner, PostProcesser, TempData


class PostWatcher(PatternMatchingEventHandler):
    def __init__(
        self,
        app: Flask,
        patterns=["*.md"],
        ignore_patterns=[".*", "_*"],
        ignore_directories=True,
        case_sensitive=True,
    ):
        super().__init__(patterns, ignore_patterns, ignore_directories, case_sensitive)
        self.logger = app.logger
        self.temp = TempData(app)

    def on_any_event(self, event):
        if event.event_type in ["created", "modified"]:
            self.logger.debug(f"{self} 检测到文件变动：{event.event_type}: {event.src_path}.")
            self.temp.add_to_update(event.src_path)

        elif event.event_type == "deleted":
            self.logger.debug(f"{self} 检测到文件变动：{event.event_type}: {event.src_path}.")
            self.temp.add_to_delete(event.src_path)

    def __str__(self) -> str:
        return self.__class__.__name__


class Watcher:
    def __init__(self, app: Flask) -> None:
        self.app = app

        self.post_watcher = PostWatcher(app)
        self.observer = Observer()

    def run(self):
        self.app.logger.info(f"{self} 启动文件监视器")
        self.observer.schedule(
            event_handler=self.post_watcher,
            path=self.app.config["POSTSPACE"],
            recursive=True,
        )

        self.observer.start()

    def __str__(self) -> str:
        return self.__class__.__name__


class Scheduler:
    def __init__(self, app: Flask) -> None:
        self.app = app

        self.watcher = Watcher(app)
        self.scheduler = BackgroundScheduler()
        self.temp = TempData(app)

    def __update_data_to_db(self):
        post_paths = self.temp.posts_to_update
        if post_paths:
            for path in post_paths:
                processer = PostProcesser(self.app, path.decode())
                with self.app.app_context():
                    processer.process()

    def __delete_data_from_db(self):
        post_paths = self.temp.posts_to_delete
        if post_paths:
            for path in post_paths:
                processer = PostCleaner(self.app, path.decode())
                with self.app.app_context():
                    processer.process()

    def run(self):
        self.app.logger.info("启动定时任务")
        self.watcher.run()

        self.scheduler.add_job(
            func=self.__update_data_to_db, trigger="interval", seconds=10
        )
        self.scheduler.add_job(
            func=self.__delete_data_from_db, trigger="interval", seconds=10
        )

        self.scheduler.start()

    def __str__(self) -> str:
        return self.__class__.__name__
