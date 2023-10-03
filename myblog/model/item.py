import os
import re
from ast import List
from datetime import date

import redis
import yaml
from flask import Flask, url_for
from markdown import markdown

from myblog.model import pool

conn = redis.Redis(connection_pool=pool)


class PersistentData:
    pass


class TempData:
    def __init__(self, app: Flask) -> None:
        self.logger = app.logger

    def add_to_update(self, path: str) -> None:
        conn.sadd("to:update", path)

    @property
    def posts_to_update(self) -> list:
        item_count = conn.scard("to:update")
        if item_count:
            self.logger.info(f"共有 {item_count} 个文章等待更新...")

        return conn.spop("to:update", item_count)


class MdTextReader:
    def __init__(self, app: Flask, path: str) -> None:
        self.logger = app.logger
        self.path = path

        self.__mdtext = self.__read_mdtext()

    def __read_mdtext(self):
        with open(self.path, "r", encoding="UTF-8") as f:
            md_text = f.read()

        if not md_text:
            self.logger.warn(f"检测到[{self.path}]文件为空.")

            return ""

        return md_text

    def __get_metadata(self):
        if not self.__mdtext:
            return {"path": self.path}

        pattern = r"---\n(.*?)\n---"
        match = re.search(pattern, self.__mdtext, re.DOTALL)
        if match:
            yaml_text = match.group(1)
            data = yaml.safe_load(yaml_text)

            data["path"] = self.path
            data["title"] = self.title
            dirname = os.path.dirname(self.path)
            self.logger.debug(f"dirname: {dirname}")

            if os.path.basename(os.path.dirname(dirname)) != "posts":
                self.logger.warn(f"检测到文章 {self.title} 并没有正确的文件夹下")
                return {"path": self.path}

            data["category"] = os.path.basename(dirname)

            self.logger.debug(f"获取{self.title}的元数据: {data}")

            return data

    def __get_mdtext_body(self):
        if not self.__mdtext:
            return ""

        pattern = r"---\n.*?\n---(.*)"
        match = re.search(pattern, self.__mdtext, re.DOTALL)
        if match:
            data = match.group(1)
            self.logger.debug(f"获取{os.path.basename(self.path)}的正文: {data[0:100]}...")
            return data

    @property
    def md_metadata(self) -> str:
        return self.__get_metadata()

    @property
    def md_body(self) -> str:
        return self.__get_mdtext_body()

    @property
    def title(self) -> str:
        result = os.path.basename(self.path).replace(".md", "").replace(" ", "")
        return result


class MetaProcesser:
    def __init__(self, app: Flask) -> None:
        self.logger = app.logger
        self.__metadata = {}
        self.__valid = False

    def set_metadata(self, md_metadata: dict) -> None:
        self.__metadata = md_metadata

    def __format_date(self) -> str:
        publish_date = self.__metadata.get("date", "")
        if not isinstance(publish_date, date):
            publish_date = date.today()

        self.__metadata["date"] = publish_date.isoformat()

    def __validate_tag(self) -> None:
        tags = self.__metadata.get("tags", "")
        self.logger.debug(f"tags: {tags}")

        if (not tags) or (not isinstance(tags, list)):
            post_path = self.__metadata["path"]
            self.logger.warn(f"检测到文章 {post_path} 没有设置标签或者不符合规范.")

            self.__valid = False

        self.__valid = True
        self.__metadata["tags"] = str(tags)

    def __format_other_values(self) -> None:
        formated_meta = {}
        for k, v in self.__metadata.items():
            formated_meta[str(k)] = str(v)

        self.__metadata = formated_meta

    @property
    def metadata(self) -> dict:
        if self.valid:
            self.__format_date()
            self.__format_other_values()

            return self.__metadata
        else:
            return {}

    @property
    def valid(self) -> bool:
        self.__validate_tag()

        return self.__valid


class BodyProcesser:
    def __init__(self, app: Flask) -> None:
        self.logger = app.logger
        self.__body = ""

        self.__valid = False

    def set_body(self, body: str) -> None:
        self.__body = body

    def __validate_body(self) -> bool:
        if self.__body:
            self.__valid = True
        else:
            self.logger.warn("检测到正文不存在！")

    def __format_body(self) -> None:
        self.__body = markdown(self.__format_image_url(self.__body))

    def __format_image_url(self, mdtext: str) -> str:
        pattern = r"!\[\[(.*?)\]\]"

        def replace(match):
            image_name = match.group(1)
            return f"![{image_name}]({image_name})"

        result = re.sub(pattern, replace, mdtext)

        return result

    @property
    def body(self) -> str:
        if self.valid:
            self.__format_body()
            return self.__body

    @property
    def valid(self) -> bool:
        self.__validate_body()

        return self.__valid


class PostProcesser:
    def __init__(self, app: Flask, mdpath: str) -> None:
        self.logger = app.logger
        self.__mdreader = MdTextReader(app, mdpath)
        self.__metaprocesser = MetaProcesser(app)
        self.__bodyprocesser = BodyProcesser(app)

    def __process(self) -> None:
        metadata = self.__metaprocesser.metadata

        post_title = metadata["title"]

        self.logger.debug(f"获取到文章 {post_title} 的元数据: {metadata},开始将其储存到redis数据库中.")

        conn.hmset(f"post:{post_title}:metadata", metadata)

        post_date_to_score = int(str(metadata["date"]).replace("-", ""))
        self.logger.debug(f"开始将文章 {post_title} 按照日期 {post_date_to_score} 放入有序列表中.")

        conn.zadd("post:recent", {metadata["title"]: post_date_to_score})

        body = self.__bodyprocesser.body

        self.logger.debug(f"开始将文章 {post_title} 正文 {body[0:30]}... 保存到数据库中.")

        conn.set(f"post:{post_title}:body", body)

        self.logger.info(f"成功处理文章 {post_title}!")

    def process(self) -> None:
        if self.valid:
            self.__process()
        else:
            self.__metaprocesser.set_metadata(self.__mdreader.md_metadata)
            metadata = self.__metaprocesser.metadata

            self.logger.warn(f"{metadata['path']} 文章格式不合法")

    @property
    def valid(self) -> bool:
        self.__metaprocesser.set_metadata(self.__mdreader.md_metadata)
        self.__bodyprocesser.set_body(self.__mdreader.md_body)

        return self.__metaprocesser.valid and self.__bodyprocesser.valid
