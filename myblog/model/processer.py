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

conn = redis.Redis(connection_pool=pool)


class TempData:
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
    def __init__(self, app: Flask) -> None:
        self.app = app
        self.__metadata = {}
        self.__valid = False

    def set_metadata(self, md_metadata: dict) -> None:
        self.__metadata = md_metadata
        self.__post_path = md_metadata["path"]

        self.app.logger.debug(f"{self} 接收元数据{type(self.__metadata)}: {self.__metadata}")

    def __format_date(self) -> str:
        publish_date = self.__metadata.get("date", "")
        if not isinstance(publish_date, date):
            publish_date = date.today()

        self.__metadata["date"] = publish_date.isoformat()

    def __validate_tag(self) -> None:
        tags = self.__metadata.get("tags", "")
        post_path = self.__metadata["path"]

        if not tags:
            self.app.logger.warn(f"{self} 检测到 {post_path} 没有设置标签: {tags}.")

        else:
            self.__valid = True

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

        self.app.logger.debug(f"{self} 处理的结果是 {type(result)}: {result}")

        return result

    @property
    def valid(self) -> bool:
        self.__validate_tag()

        return self.__valid

    def __str__(self) -> str:
        return f"{self.__class__.__name__}"


class BodyProcesser:
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

    def __format_body(self) -> None:
        self.__body = markdown(self.__format_image_url(self.__body))

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
    def body(self) -> str:
        if self.valid:
            self.__format_body()
            return self.__body

    @property
    def valid(self) -> bool:
        self.__validate_body()

        return self.__valid

    def __str__(self) -> str:
        return self.__class__.__name__


class PostProcesser:
    def __init__(self, app: Flask, mdpath: str) -> None:
        self.app = app
        self.__mdreader = MdTextReader(app, mdpath)
        self.__metaprocesser = MetaProcesser(app)
        self.__bodyprocesser = BodyProcesser(app)

    def __process(self) -> None:
        metadata = self.__metaprocesser.metadata
        post_title = metadata["title"]
        post_date_to_score = int(str(metadata["date"]).replace("-", ""))
        body = self.__bodyprocesser.body

        conn.hmset(f"post:{post_title}:metadata", metadata)

        conn.zadd("post:recent", {metadata["title"]: post_date_to_score})

        conn.set(f"post:{post_title}:body", body)

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
        body = self.__bodyprocesser.body

        if not meta_valid:
            self.app.logger.warn(
                f"{self} 检测到文章 {metadata['path']} 的元数据不符合规定, metadata: {type(metadata)}: {metadata}"
            )

        if not body_valid:
            self.app.logger.warn(
                f"{self} 检测到文章 {metadata['path']} 的正文不符合规定, body: {type(body)}: {body}"
            )

        return meta_valid and body_valid

    def __str__(self) -> str:
        return f"{self.__class__.__name__}"


class PostCleaner:
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

        try:
            metadata_name = f"post:{post_title}:metadata"
            body_name = f"post:{post_title}:body"

            pipe = conn.pipeline()
            pipe.zrem("post:recent", post_title)
            pipe.delete(*[metadata_name, body_name])
            pipe.execute()

            self.app.logger.debug(f"{self} 成功将 {post_title} 从数据库中删除。")

        except:
            self.app.logger.warn(f"{self} 在删除数据的过程中出现故障！")

    def process(self) -> None:
        if not self.__verify_in_dir() and self.__verify_indb():
            self.__delete_post_from_db()

    def __str__(self) -> str:
        return self.__class__.__name__


class WritingSpaceReader:
    def __init__(self, app: Flask) -> None:
        self.app = app

    def __get_config_path(self) -> str:
        path = os.path.join(self.app.config["WRITINGSPACE"])
        if not os.path.exists(path):
            raise FileNotFoundError(
                f"{self} 检测到写作空间 {self.app.config['DATA_DIR']} 内不存在配置文件 writingspace.json"
            )
        return path

    def __get_dict_config(self) -> dict:
        with open(self.__get_config_path(), "r", encoding="UTF-8") as f:
            dict_config = json.load(f)
        if dict_config:
            self.app.logger.debug(
                f"{self} 获取到 writingspace.json 的数据 {type(dict_config)}: {dict_config}"
            )
        else:
            raise FileError(f"{self} 检测到到 writingspace.json 的数据为空")

        return dict_config

    @property
    def data(self) -> dict:
        return self.__get_dict_config()

    @property
    def home_path(self) -> str:
        temp = str(self.data["path"]["homePostPath"]).split("/")
        home_post_path = os.path.join(self.app.config["DATA_DIR"], *temp)

        if not os.path.exists(home_post_path):
            raise FileNotFoundError(f"{self} 没有找到首页文章")
        elif not home_post_path.endswith(".md"):
            raise Exception(f"{self} 检测到首页文章不是 markdown 类型的文章")

        return home_post_path

    def __str__(self) -> str:
        return self.__class__.__name__
