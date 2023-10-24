"""
职责：从数据库中加载数据
被谁使用：视图函数以及模板
"""

import os
from datetime import date, datetime
from typing import Dict, Union

from flask import Flask

from myblog.model import MySQLHandler
from myblog.model.utlis import get_data_from_json_file
from myblog.model.validator import ProfileValidator


class ProfileLoader:
    """
    职责：从指定文件中加载用户的简历数据
    """

    def __init__(self, app: Flask) -> None:
        self.app = app
        self.validator = ProfileValidator(app)
        self.path = self.__get_profile_path()

        self.__data = {
            "author": {
                "name": "作者名称",
                "brith_date": date.today().isoformat(),
                "email": "example@example.com",
                "github": None,
                "motto": None,
            },
            "website": {
                "title": "MYBLOG",
                "subtitle": None,
                "building_time": date.today().isoformat(),
                "description": "这是我的个人网站",
            },
            "content": {"trend_repo": []},
        }

    def __get_profile_path(self) -> str:
        PATH_WORKTREE_USERDATA = os.getenv("PATH_WORKTREE_USERDATA")
        profile_path = os.path.join(PATH_WORKTREE_USERDATA, "profile.json")

        return profile_path

    def __load_data(self) -> None:
        if os.path.exists(self.path):
            profile = get_data_from_json_file(self.path)

            self.validator.set(profile)

            if self.validator.validate():
                self.__data.update(profile)
            else:
                self.app.logger.warn("profile.json 内容不符合规范，无法更新 profile 信息！")

    @property
    def data(self) -> dict:
        self.__load_data()

        return self.__data


class TrendLoader:
    """
    职责：从数据库中加载动态数据
    接收一个 id 列表，返回一个 trend 列表
    """

    def __init__(self, app: Flask) -> None:
        self.app = app
        self.mysql: MySQLHandler = app.config["MYSQL_HANDLER"]
        self.mysql.connect()

        self.__data: list[dict] = []

        self.__item: dict[str, Union[str, datetime]] = {
            "id": "",
            "title": "",
            "body": "",
            "time": None,
            "project": "",
            "author_name": "",
            "author_email": "",
        }

    def set(self, *trend_ids) -> None:
        self.trend_ids = trend_ids

    def __load_trend_data(self) -> None:
        """
        默认排序是从新到旧
        """
        sql: str = """
        SELECT id, title, body, time, project, author_name, author_email
        FROM trend
        WHERE id IN ({})
        ORDER BY time DESC
        """

        data = self.mysql.execute_query(
            sql.format(",".join(["'{}'".format(tid) for tid in self.trend_ids]))
        )
        result = []

        for d in data:
            item = {}
            for k, v in zip(self.__item.keys(), d):
                item[k] = v
            result.append(item)

        self.__data = result

    def recent(self, count: int) -> list[dict[str, Union[str, datetime]]]:
        sql: str = "SELECT * FROM trend ORDER BY time DESC LIMIT {count};".format(
            count=count
        )
        data = self.mysql.execute_query(sql)
        result = []

        for d in data:
            item = {}
            for k, v in zip(self.__item.keys(), d):
                item[k] = v
            result.append(item)

        return result

    @property
    def data(self) -> list[dict[str, Union[str, datetime]]]:
        self.__load_trend_data()

        return self.__data


class PostLoader:
    """
    职责：从数据库中加载文章数据
    """

    def __init__(self, app: Flask) -> None:
        self.app = app
        self.mysql: MySQLHandler = app.config["MYSQL_HANDLER"]
        self.mysql.connect()

        self.__data: Dict[str, Union[str, date, "PostLoader", None]] = {
            "id": "",
            "title": "",
            "author": "",
            "body": "",
            "toc": "",
            "path": "",
            "date": None,
            "updated": None,
            "summary": "",
            "category": "",
            "newer": None,
            "older": None,
        }

    def set(self, post_id: str) -> None:
        self.post_id = post_id

    def __load_current_post(self) -> None:
        sql: str = """
SELECT id, title, author, body, toc, path, date, updated, summary, category 
FROM post 
WHERE id='{post_id}'
"""
        data: tuple = self.mysql.execute_query(sql.format(post_id=self.post_id))[0]

        for k, v in zip(self.__data.keys(), data):
            self.__data[k] = v

    def __load_nearby_post(self) -> None:
        """
        职责：加载相对于当前文章的前一个和后一个文章对象
        """
        sql: str = """
SELECT id
FROM post
ORDER BY date ASC;
"""
        result = self.mysql.execute_query(sql)

        id_list = [t[0] for t in result]

        current_index = id_list.index(self.post_id)

        if current_index == len(id_list) - 1:
            self.app.logger.debug("当前文章已经是最新文章。")
            self.__data["newer"] = None
        else:
            post = PostLoader(self.app)
            post.set(id_list[current_index + 1])
            self.__data["newer"] = post

        if current_index == 0:
            self.app.logger.debug("当前文章已经是最早文章。")
            self.__data["older"] = None
        else:
            post = PostLoader(self.app)
            post.set(id_list[current_index - 1])
            self.__data["older"] = post

    def recent(self, count: int) -> list[dict[str, Union[str, date, None]]]:
        """
        职责：加载指定数量的最近文章
        """
        sql: str = "SELECT * FROM post ORDER BY date DESC LIMIT {count};".format(
            count=count
        )
        data: tuple = self.mysql.execute_query(sql)

        result = []

        for d in data:
            item = {}
            for k, v in zip(self.__data.keys(), d):
                item[k] = v
            result.append(item)

        return result

    @property
    def data(self) -> Dict[str, Union[str, date, "PostLoader", None]]:
        self.__load_current_post()
        self.__load_nearby_post()

        return self.__data
