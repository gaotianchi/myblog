"""
职责：控制器，负责调度各个模块
"""

import os

from flask import Flask

from myblog.model.dbupdater import PostCleaner, PostDbUpdater
from myblog.model.processer import BodyProcesser, MetadataProcesser
from myblog.model.utlis import generate_id
from myblog.model.validator import PostValidatorFactory


class PostUpdater:

    """
    职责：更新数据库文章，添加，更新以及删除
    """

    def __init__(self, app: Flask) -> None:
        self.app = app

        self.validator = PostValidatorFactory(app)
        self.metaprocesser = MetadataProcesser(app)
        self.bodyprocesser = BodyProcesser(app)
        self.updater = PostDbUpdater(app)
        self.cleaner = PostCleaner(app)

    def set(self, path: str, t: str) -> None:
        self.p = path
        self.t = t

    def __process(self) -> None:
        pathvalidator = self.validator.get_validator("postpath")
        pathvalidator.set(self.p)
        if not pathvalidator.validate():
            return None

        if self.t == "D":
            post_title: str = os.path.basename(self.p).replace(".md", "")
            post_id: str = generate_id(post_title)
            self.cleaner.set(post_id)
            self.cleaner.delete()
            self.app.logger.debug(f"文章{os.path.basename(self.p)}被成功删除.")

            return None

        metavalidator = self.validator.get_validator("postmetadata")
        bodyvalidator = self.validator.get_validator("postbody")

        md_text: str = self.__get_md_text(self.p)

        metavalidator.set(md_text)
        bodyvalidator.set(md_text)

        if metavalidator.validate() and bodyvalidator.validate():
            self.metaprocesser.set(md_text, self.p)
            self.bodyprocesser.set(md_text)

            metadata = self.metaprocesser.data
            body_items = self.bodyprocesser.data
            post_items: dict = dict(metadata=metadata, body_items=body_items)

            self.updater.set(post_items)
            self.updater.update()
            self.app.logger.debug(f"文章{os.path.basename(self.p)}更新完成.")

    def __get_md_text(self, path: str) -> str:
        with open(path, "r", encoding="UTF-8") as f:
            md_text = f.read()

        return md_text.strip()

    def update(self) -> None:
        self.__process()
