"""
职责：提供数据验证服务
"""

import os
import re
from abc import ABC, abstractmethod
from datetime import date, datetime

from flask import Flask
from markdown import Markdown

from myblog.model.utlis import get_meta_and_body, get_summary_and_body


class Validator(ABC):
    @abstractmethod
    def set(self):
        pass

    @abstractmethod
    def validate(self):
        pass

    def __str__(self) -> str:
        return self.__class__.__name__


class TrendValidator(Validator):
    def __init__(self, app: Flask) -> None:
        self.app = app
        self.__valid = False

    def set(self, commit_item: dict):
        self.summary = get_summary_and_body(commit_item["message"])["summary"]
        self.body = get_summary_and_body(commit_item["message"])["body"]
        self.time = commit_item["time"]

    def __validate_datetime(self) -> bool:
        if not isinstance(self.time, datetime):
            return False

        return True

    def __validate_word_count(self) -> bool:
        TREND_BODY_MIN_WORD_COUNT: int = self.app.config["TREND_BODY_MIN_WORD_COUNT"]
        TREND_BODY_MAX_WORD_COUNT: int = self.app.config["TREND_BODY_MAX_WORD_COUNT"]

        TREND_SUMMARY_MIN_WORD_COUNT: int = self.app.config[
            "TREND_SUMMARY_MIN_WORD_COUNT"
        ]
        TREND_SUMMARY_MAX_WORD_COUNT: int = self.app.config[
            "TREND_SUMMARY_MAX_WORD_COUNT"
        ]

        summary_word_count = len(self.summary)
        body_word_count = len(self.body)

        if summary_word_count > TREND_SUMMARY_MAX_WORD_COUNT:
            self.app.logger.warn(
                f"summary 字数{summary_word_count}超出最大限制 {TREND_SUMMARY_MAX_WORD_COUNT}"
            )
            return False
        elif summary_word_count < TREND_SUMMARY_MIN_WORD_COUNT:
            self.app.logger.warn(
                f"summary 字数{summary_word_count} 低于最小限制 {TREND_SUMMARY_MIN_WORD_COUNT}"
            )
            return False

        if body_word_count > TREND_BODY_MAX_WORD_COUNT:
            self.app.logger.warn(
                f"body 字数{body_word_count}超出最大限制 {TREND_BODY_MAX_WORD_COUNT}"
            )
            return False
        elif body_word_count < TREND_BODY_MIN_WORD_COUNT:
            self.app.logger.warn(
                f"body 字数{summary_word_count} 低于最小限制 {TREND_BODY_MIN_WORD_COUNT}"
            )
            return False

        return True

    def __validate_whether_to_publish(self) -> bool:
        """
        职责：根据日志消息中的 TREND_PUBLISH_SINGAL 判断是否发布
        当正文部分位置出现 #publish 时发布消息
        """
        TREND_PUBLISH_SINGAL = self.app.config["TREND_PUBLISH_SINGAL"]

        matches = re.findall(r"%s" % TREND_PUBLISH_SINGAL, self.body, re.DOTALL)
        if not matches:
            return False

        return True

    def validate(self):
        self.__valid = (
            self.__validate_word_count()
            and self.__validate_whether_to_publish()
            and self.__validate_datetime()
        )

        return self.__valid


class PostPathValidator(Validator):
    """
    职责：验证文章的位置是否符合规范
    被谁使用：文章处理器
    """

    def __init__(self, app: Flask) -> None:
        self.app = app
        self.__valid = False

    def set(self, path: str) -> None:
        self.path = path

    def __validate_file_format(self) -> bool:
        if not self.path.endswith(".md"):
            return False

        return True

    def __validate_loacation(self) -> bool:
        PATH_POST = os.path.join(os.getenv("PATH_WORKTREE_USERDATA"), "文章")
        path = os.path.dirname(os.path.dirname(self.path))

        if not PATH_POST == path:
            self.app.logger.warn(f"文章没有放到正确的目录下: {os.path.basename(path)}")

            return False

        return True

    def __validate(self) -> None:
        self.__valid = self.__validate_file_format() and self.__validate_loacation()

    def validate(self) -> bool:
        self.__validate()

        return self.__valid


class PostMetadataValidator(Validator):
    """
    职责：验证文章的元数据是否符合规范
    """

    def __init__(self, app: Flask) -> None:
        self.app = app
        self.__valid = False

    def set(self, md_text: str) -> None:
        self.meta: dict = get_meta_and_body(md_text)["metadata"]

    def __validate_required_key(self) -> bool:
        """
        职责：验证必需的元数据的数据类型
        """
        REQUIRED_POST_KEY: dict = self.app.config["REQUIRED_POST_KEY"]
        keys = self.meta.keys()
        missing_keys = set(REQUIRED_POST_KEY.keys()) - (
            set(REQUIRED_POST_KEY.keys()) & set(keys)
        )

        if missing_keys:
            self.app.logger.warn(f"缺失元数据: {missing_keys}!")
            return False

        invalid_metadata = []
        for k, t in REQUIRED_POST_KEY.items():
            if not isinstance(self.meta.get(k), t):
                invalid_metadata.append(k)

        if invalid_metadata:
            self.app.logger.warn(f"元数据的数据类型异常: {invalid_metadata}")
            return False

        return True

    def __valdate_date_format(self) -> bool:
        if not self.meta.get("date", ""):
            return False

        if not isinstance(self.meta["date"], date):
            return False

        return True

    def __validate(self) -> None:
        self.__valid = self.__validate_required_key() and self.__valdate_date_format()

    def validate(self) -> bool:
        self.__validate()

        return self.__valid


class PostBodyValidator(Validator):
    """
    职责：验证文章的正文是否符合规范
    """

    def __init__(self, app: Flask) -> None:
        self.app = app
        self.__valid = False

    def set(self, md_text: str) -> None:
        self.body = get_meta_and_body(md_text)["body"]

    def __validate_table(self) -> None:
        md = Markdown(extensions=["toc"])
        md.convert(self.body)
        table: str = md.toc
        unexpected_html = '<divclass="toc"><ul></ul></div>'

        if table.replace("\n", "").replace(" ", "") == unexpected_html:
            self.app.logger.warn(f"文章缺失目录: {self.body[0:50]}...")
            return False

        return True

    def __validate(self) -> None:
        if self.body and self.__validate_table():
            self.__valid = True

    def validate(self) -> bool:
        self.__validate()

        return self.__valid


class ValidatorFactory:
    def __init__(self, app: Flask) -> None:
        self.app = app

    def get_validator(self, name: str) -> Validator:
        match name:
            case "postpath":
                return PostPathValidator(self.app)
            case "postmetadata":
                return PostMetadataValidator(self.app)
            case "postbody":
                return PostBodyValidator(self.app)
            case "trend":
                return TrendValidator(self.app)
