import unittest
from datetime import datetime

from flask import Flask

from myblog.model import MySQLHandler
from myblog.model.itemloader import TrendLoader
from myblog.setting import config


class TrendLoaderTestCase(unittest.TestCase):
    def setUp(self) -> None:
        mysql_config = config["base"].MYSQL_CONFIG
        mysql_config["database"] = "test_db_trendloader"
        app = Flask(__name__)
        app.config["MYSQL_HANDLER"] = MySQLHandler(**mysql_config)

        self.loader = TrendLoader(app)

        self.loader.mysql.execute_update(
            """
CREATE TABLE IF NOT EXISTS trend (
  id VARCHAR(30) PRIMARY KEY,
  title VARCHAR(300),
  body TEXT,
  time DATETIME,
  project VARCHAR(255),
  author_name VARCHAR(30),
  author_email VARCHAR(255)
);
"""
        )
        time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.loader.mysql.execute_update(
            """
INSERT INTO
  trend (id, title, body, time, project, author_name, author_email)
VALUES
('kkjkkjkkjd', '你好世界', '你好你好世界你好世界你好世界', '%s', '项目名称', '高天驰', '6159984@gmail.com')
"""
            % time
        )

    def tearDown(self) -> None:
        self.loader.mysql.execute_update("DROP DATABASE IF EXISTS test_db_trendloader")

    def test_data(self):
        self.loader.set("kkjkkjkkjd")
        data = self.loader.data[0]
        self.assertEqual(data["title"], "你好世界")
        self.assertEqual(data["body"], "你好你好世界你好世界你好世界")
        self.assertTrue(isinstance(data["time"], datetime))

    def test_recent(self):
        data = self.loader.recent(1)[0]
        self.assertEqual(data["title"], "你好世界")
        self.assertEqual(data["body"], "你好你好世界你好世界你好世界")
        self.assertTrue(isinstance(data["time"], datetime))
