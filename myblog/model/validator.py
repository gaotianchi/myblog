"""
职责：提供数据验证服务
"""

import os
from abc import ABC, abstractmethod
from datetime import date

from flask import Flask
from markdown import Markdown

from myblog.model.utlis import get_meta_and_body


class Validator(ABC):
    @abstractmethod
    def set(self):
        pass

    @abstractmethod
    def validate(self):
        pass

    def __str__(self) -> str:
        return self.__class__.__name__


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


class PostValidatorFactory:
    def __init__(self, app: Flask) -> None:
        self.app = app

    def get_validator(self, name: str) -> Validator:
        if name.lower() not in ["postpath", "postmetadata", "postbody"]:
            raise "请输入正确的验证器名称"

        match name:
            case "postpath":
                return PostPathValidator(self.app)
            case "postmetadata":
                return PostMetadataValidator(self.app)
            case "postbody":
                return PostBodyValidator(self.app)
