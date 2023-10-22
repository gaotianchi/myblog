"""
职责：从数据库中加载数据
被谁使用：视图函数以及模板
"""

from datetime import date
from typing import Dict, Union

from flask import Flask

from myblog.model import MySQLHandler


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

    @property
    def data(self) -> Dict[str, Union[str, date, "PostLoader", None]]:
        self.__load_current_post()
        self.__load_nearby_post()

        return self.__data
