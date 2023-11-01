"""
职责：负责更新数据库
"""


from flask import Flask

from myblog.model import MySQLHandler


class TrendDbUpdater:
    """
    职责：更新、写入动态到数据库
    前置条件：动态数据已经经过处理器处理
    """

    def __init__(self, app: Flask) -> None:
        self.app = app
        self.mysql: MySQLHandler = app.config["MYSQL_HANDLER"]

        self.mysql.connect()

        self.__init_table()

    def set(self, trend: dict) -> None:
        self.trend = trend

    def __init_table(self) -> None:
        """
        职责：检查文章表是否存在，如果不存在则创建
        """
        self.mysql.execute_update(
            """
CREATE TABLE IF NOT EXISTS trend (
  id INT AUTO_INCREMENT PRIMARY KEY,
  title VARCHAR(300),
  body TEXT,
  time DATETIME,
  project VARCHAR(255),
  author_name VARCHAR(30),
  author_email VARCHAR(255)
);
"""
        )

    def __insert_trend(self) -> None:
        """
        职责：向数据库写入动态数据
        """
        sql: str = """
INSERT INTO
  trend (title, body, time, project, author_name, author_email)
VALUES
  ('{title}', '{body}', '{time}', '{project}', '{author_name}', '{author_email}')
"""
        self.mysql.execute_update(sql.format(**self.trend))

    def update(self) -> None:
        self.__insert_trend()


class PostDbUpdater:
    """
    职责：负责更新、写入文章数据库
    """

    def __init__(self, app: Flask) -> None:
        self.app = app
        self.mysql: MySQLHandler = app.config["MYSQL_HANDLER"]

        self.mysql.connect()

        self.__init_table()

    def set(self, post_items: dict) -> None:
        self.metadata: dict = post_items["metadata"]
        self.body_items: dict = post_items["body_items"]

    def update(self) -> None:
        """
        职责：主程序
        """
        if self.__key_is_exist():
            self.__update_post()
        else:
            self.__insert_post()

    def __update_post(self) -> None:
        """
        职责：更新文章数据
        """
        sql: str = """
    UPDATE 
        post
    SET 
        id = '{id}', 
        title = '{title}', 
        author = '{author}', 
        body = '{body}', 
        toc = '{toc}', 
        path = '{path}', 
        date = '{date}', 
        updated = '{updated}',
        summary = '{summary}',
        category = '{category}'
    WHERE
        id = '{id}'
    """
        self.mysql.execute_update(sql.format(**self.body_items, **self.metadata))

    def __insert_post(self) -> None:
        """
        职责：写入文章数据
        """
        sql: str = """
    INSERT INTO 
        post (id, title, author, body, toc, path, date, updated, summary, category)
    VALUES 
        ('{id}', '{title}', '{author}', '{body}', '{toc}', '{path}', '{date}', '{updated}', '{summary}', '{category}')
    """
        self.mysql.execute_update(sql.format(**self.body_items, **self.metadata))

    def __init_table(self) -> None:
        """
        职责：检查文章表是否存在，如果不存在则创建
        """
        self.mysql.execute_update(
            """
CREATE TABLE IF NOT EXISTS post (
  id VARCHAR(30) PRIMARY KEY,
  title VARCHAR(60),
  author VARCHAR(30),
  body TEXT,
  toc TEXT,
  path VARCHAR(255),
  date DATE,
  updated DATE,
  summary TINYTEXT,
  category VARCHAR(30)
);
"""
        )

    def __key_is_exist(self) -> bool:
        """
        职责：根据文章 ID 判断文章在数据库中是否存在
        """
        post_id: str = self.metadata["id"]
        try:
            result = self.mysql.execute_query(
                "SELECT id FROM post WHERE id='{post_id}'".format(post_id=post_id)
            )
            if result:
                return True
        except:
            return False


class PostCleaner:
    """
    职责：负责从数据库中清除指定文章
    """

    def __init__(self, app: Flask) -> None:
        self.app = app
        self.mysql: MySQLHandler = app.config["MYSQL_HANDLER"]

        self.mysql.connect()

    def set(self, post_id: str) -> None:
        self.id = post_id

    def __key_is_exist(self) -> bool:
        """
        职责：根据文章 ID 判断文章在数据库中是否存在
        """
        try:
            result = self.mysql.execute_query(
                "SELECT id FROM post WHERE id='{post_id}'".format(post_id=self.id)
            )
            if result:
                return True
        except:
            return False

    def __delete_post(self) -> None:
        """
        职责：将文章从数据库中删除
        """
        sql: str = "DELETE FROM post WHERE id='{post_id}'".format(post_id=self.id)

        self.mysql.execute_update(sql)

    def delete(self) -> None:
        if self.__key_is_exist():
            self.__delete_post()
