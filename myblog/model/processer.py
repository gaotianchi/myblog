import json
import os
import re
from datetime import date

import redis
import yaml
from click import FileError
from flask import Flask, current_app, url_for
from markdown import markdown

from myblog.model import pool
from myblog.utlis import generate_id

conn = redis.Redis(connection_pool=pool)


class TempData:
    """
    职责：储存临时数据，并在使用后销毁。
    使用者：
        1. scheduler.WritingSpaceWatcher
        2. scheduler.Scheduler
    """

    def __init__(self, app: Flask) -> None:
        self.app = app

    def add_to_update(self, path: str) -> None:
        conn.sadd("to:update", path)

    def add_to_delete(self, path: str) -> None:
        conn.sadd("to:delete", path)

    @property
    def posts_to_update(self) -> list:
        item_count = conn.scard("to:update")
        if item_count:
            self.app.logger.debug(f"{self} 检测到共有 {item_count} 个文章等待更新...")

        return conn.spop("to:update", item_count)

    @property
    def posts_to_delete(self) -> list:
        item_count = conn.scard("to:delete")
        if item_count:
            self.app.logger.debug(f"{self} 检测到共有 {item_count} 个文章等待删除...")

        return conn.spop("to:delete", item_count)

    def __str__(self) -> str:
        return self.__class__.__name__


class MdTextReader:
    """
    职责：读取 .md 文件，返回文件内容。
    使用者：
        1. processer.PostProcesser
    """

    def __init__(self, app: Flask, path: str) -> None:
        self.app = app
        self.path = path

        self.__mdtext = self.__read_mdtext()

    def __read_mdtext(self):
        with open(self.path, "r", encoding="UTF-8") as f:
            md_text = f.read()

        if not md_text:
            self.app.logger.warn(f"{self} 检测到[{self.path}]文件为空.")

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
            postdir = self.app.config["POSTSPACE"]
            dirname = os.path.dirname(self.path)

            if os.path.abspath(os.path.dirname(dirname)) != postdir:
                self.app.logger.warn(f"{self} 检测到文章的位置不符合规定，请将文章放在某个以类别命名的文件夹下！")
                return {"path": self.path}

            data["category"] = os.path.basename(dirname)

            return data

    def __get_mdtext_body(self):
        if not self.__mdtext:
            return ""

        pattern = r"---\n.*?\n---(.*)"
        match = re.search(pattern, self.__mdtext, re.DOTALL)
        if match:
            data = match.group(1)
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

    def __str__(self) -> str:
        return self.__class__.__name__


class MetaProcesser:
    """
    职责：获取、验证然后返回文章的元数据。
    使用者：
        1. processer.PostProcesser
    """

    def __init__(self, app: Flask) -> None:
        self.app = app
        self.__metadata = {}

    def set_metadata(self, md_metadata: dict) -> None:
        self.__metadata = md_metadata
        self.__post_path = md_metadata["path"]

    def __format_date(self):
        publish_date = self.__metadata.get("date", "")

        if isinstance(publish_date, date):
            self.__metadata["date"] = publish_date.isoformat()
            return

        if not re.match(r"\d{4}-\d{2}-\d{2}", publish_date):
            publish_date = date.today()
            self.__metadata["date"] = publish_date.isoformat()
            return

    def __validate_tag(self) -> None:
        tags = self.__metadata.get("tags", "")
        post_path = self.__metadata["path"]

        if not tags:
            self.app.logger.warn(f"{self} 检测到 {post_path} 没有设置标签: {tags}.")
            return False
        else:
            return True

    def __validate_summary(self) -> None:
        summary: str = self.__metadata.get("summary", "")
        post_path = self.__metadata["path"]

        if not summary:
            self.app.logger.warn(f"{self} 检测到 {post_path} 没有设置摘要！")
            return False
        else:
            return True

    def __format_other_values(self) -> None:
        formated_meta = {}
        for k, v in self.__metadata.items():
            formated_meta[str(k)] = str(v)

        self.__metadata = formated_meta

    @property
    def metadata(self) -> dict:
        result = {}
        if self.valid:
            self.__format_date()
            self.__format_other_values()

            result = self.__metadata
        else:
            result = {"path": self.__post_path}

        return result

    @property
    def valid(self) -> bool:
        return self.__validate_summary() and self.__validate_tag()

    def __str__(self) -> str:
        return f"{self.__class__.__name__}"


class BodyProcesser:
    """
    职责：文章正文处理器，获取、验证最终返回文章正文
    使用者：
        1. processer.PostProcesser
    """

    toc_class = "sticky-top p-3 mb-3 bg-light rounded"

    def __init__(self, app: Flask) -> None:
        self.app = app
        self.__body = ""

        self.__valid = False

    def set_body(self, body: str) -> None:
        self.__body = body

    def __validate_body(self) -> bool:
        if self.__body:
            self.__valid = True
        else:
            self.app.logger.warn(f"{self} 检测到正文不存在！")

    def __check_table(self) -> None:
        pattern = f'<div class="{self.toc_class}">.*?</div>'
        matches = re.findall(pattern, self.__body, re.DOTALL)

        if not matches:
            self.app.logger.warn(f"{self} 检测到本文没有添加目录，准备添加目录")
            self.__body = "[TOC]" + "\n" + self.__body

    def __format_body(self) -> None:
        exten_config = {
            "toc": {"baselevel": 2, "permalink": "#", "toc_class": f"{self.toc_class}"},
            "footnotes": {
                "BACKLINK_TEXT": "&#8617;&#xFE0E;",
                "BACKLINK_TITLE": "回到原文被引用的地方",
            },
        }

        self.__body = markdown(
            self.__format_image_url(self.__body),
            extensions=["toc", "fenced_code", "footnotes", "nl2br"],
            extension_configs=exten_config,
        )

    def __format_image_url(self, mdtext: str) -> str:
        pattern = r"!\[\[(.*?)\]\]"

        def replace(match):
            image_name = match.group(1)
            with current_app.app_context():
                image_url = url_for("api.image", image_name=image_name)

            return f"![{image_name}]({image_url})"

        result = re.sub(pattern, replace, mdtext)

        return result

    @property
    def table_and_body(self) -> str:
        if self.valid:
            self.__check_table()
            self.__format_body()

            return self.__body

    @property
    def table(self) -> str:
        if self.valid:
            self.__format_body()
            pattern = f'<div class="{self.toc_class}">.*?</div>'
            matches = re.findall(pattern, self.table_and_body, re.DOTALL)

            if matches:
                pattern = f'<div class="{self.toc_class}">'
                div_start = re.findall(pattern, matches[0], re.DOTALL)[0]
                table_title = """
                <h4 class="font-italic">文章目录</h4>
                """
                table = re.sub(div_start, div_start + table_title, matches[0])
                return table

            else:
                self.app.logger.debug(f"{self} 检测到本文没有配置目录")

                return ""

    @property
    def body(self) -> str:
        if self.valid:
            toc_class = self.toc_class
            pattern = r'<div class="%s">.*?</div>|\[TOC\]' % toc_class

            body = re.sub(pattern, "", self.table_and_body, 0, re.DOTALL)

            return body.strip()

    @property
    def valid(self) -> bool:
        self.__validate_body()

        return self.__valid

    def __str__(self) -> str:
        return self.__class__.__name__


class PostProcesser:
    """
    职责：该类是文章元素的中心处理器，集成所有文章处理子系统，验证文章对象的是否符合规定，将子系统的处理结果储存到数据库中。
    使用者：
        1. scheduler.Scheduler
    """

    def __init__(self, app: Flask, mdpath: str) -> None:
        self.app = app
        self.__mdreader = MdTextReader(app, mdpath)
        self.__metaprocesser = MetaProcesser(app)
        self.__bodyprocesser = BodyProcesser(app)

    def __process(self) -> None:
        metadata = self.__metaprocesser.metadata
        post_id = generate_id(metadata["title"])
        post_date_to_score = int(str(metadata["date"]).replace("-", ""))
        body = self.__bodyprocesser.body
        table = self.__bodyprocesser.table
        updated = str(date.today())
        metadata["updated"] = updated
        metadata["author"] = "高天驰"

        conn.hmset(f"post:{post_id}:metadata", metadata)

        conn.zadd("post:recent", {post_id: post_date_to_score})

        conn.set(f"post:{post_id}:body", body)
        conn.set(f"post:{post_id}:table", table)

    def process(self) -> None:
        if self.valid:
            self.app.logger.debug(f"{self} 检测到元数据和正文部分全都有效，可以进行下一步的处理。")
            self.__process()

    @property
    def valid(self) -> bool:
        self.__metaprocesser.set_metadata(self.__mdreader.md_metadata)
        self.__bodyprocesser.set_body(self.__mdreader.md_body)

        meta_valid = self.__metaprocesser.valid
        body_valid = self.__bodyprocesser.valid

        metadata = self.__metaprocesser.metadata

        if not meta_valid:
            self.app.logger.warn(f"{self} 检测到文章 {metadata['path']} 的元数据不符合规定！")

        if not body_valid:
            self.app.logger.warn(f"{self} 检测到文章 {metadata['path']} 的正文不符合规定！")

        return meta_valid and body_valid

    def __str__(self) -> str:
        return f"{self.__class__.__name__}"


class PostCleaner:
    """
    职责：从数据库中删除文章相关内容
    使用者：
        1. scheduler.Scheduler
    """

    def __init__(self, app: Flask, path: str) -> None:
        self.app = app
        self.path = path

    def __verify_indb(self) -> bool:
        in_db = True
        dirname = os.path.dirname(self.path)
        if dirname == self.app.config["POSTSPACE"]:
            self.app.logger.debug(f"{self} 检测到 {self.path} 因位置错误并没有被数据库储存.")
            in_db = False

        return in_db

    def __verify_in_dir(self) -> bool:
        in_dir = False
        if os.path.exists(self.path):
            self.app.logger.debug(f"{self} 检测到 {self.path} 并没有从文件夹中移除.")
            in_dir = True
        return in_dir

    def __delete_post_from_db(self) -> None:
        post_title = os.path.basename(self.path).replace(".md", "").replace(" ", "")

        self.app.logger.debug(f"{self} 准备将 {post_title} 从数据库中删除")
        post_id = generate_id(post_title)

        try:
            metadata_name = f"post:{post_id}:metadata"
            body_name = f"post:{post_id}:body"
            table_name = f"post:{post_id}:table"

            pipe = conn.pipeline()
            pipe.zrem("post:recent", post_id)
            pipe.delete(*[metadata_name, body_name, table_name])
            pipe.execute()

            self.app.logger.debug(f"{self} 成功将 {post_title} 从数据库中删除。")

        except:
            self.app.logger.warn(f"{self} 在删除数据的过程中出现故障！")

    def process(self) -> None:
        if not self.__verify_in_dir() and self.__verify_indb():
            self.__delete_post_from_db()

    def __str__(self) -> str:
        return self.__class__.__name__


class ProfileReader:
    """
    职责：读取用户文件夹中的 profile.json 文件，并返回该文件的数据
    使用者：
        1. item.Profile
    """

    def __init__(self, app: Flask) -> None:
        self.app = app
        self.__path = os.path.join(app.config["USERDATA_DIR"], "profile.json")

    def __check_path(self) -> bool:
        if not os.path.exists(self.__path):
            filename = os.path.basename(self.__path)
            self.app.logger.warn(f"{self} 检测到用户文件夹中缺失 {filename} 文件！")

        return True

    def __get_data(self) -> dict:
        data = {}
        if self.__check_path():
            with open(self.__path, "r", encoding="UTF-8") as f:
                data = json.load(f)

        return data

    def __check_element(self):
        required_elements: list = self.app.config["PROFILE_REQUIRE_ELEMENTS"].split(",")
        data = self.__get_data()

        if not data:
            self.app.logger.warn(f"{self} 检测到 profile.json 中数据为空！")

            return False

        missing_field = set(required_elements) - (set(data) & set(required_elements))
        if missing_field:
            self.app.logger.warn(f"{self} 检测到 profile.json 缺失以下字段 {missing_field}")

            return False

        return True

    @property
    def data(self) -> dict:
        data = {}
        if self.__check_element():
            return self.__get_data()

        return data

    def __str__(self) -> str:
        return self.__class__.__name__
