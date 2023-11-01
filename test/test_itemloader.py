import unittest
from datetime import date, datetime

from flask import Flask

from myblog.model import MySQLHandler
from myblog.model.itemloader import PostLoader, ProfileLoader, TrendLoader
from myblog.model.utlis import get_data_from_json_file
from myblog.model.validator import ProfileValidator
from myblog.setting import config


class PostLoaderTestCase(unittest.TestCase):
    def setUp(self) -> None:
        mysql_config = config["base"].MYSQL_CONFIG
        mysql_config["database"] = "test_db_postloader"
        app = Flask(__name__)
        app.config["MYSQL_HANDLER"] = MySQLHandler(**mysql_config)

        self.loader = PostLoader(app)

        self.loader.mysql.execute_update(
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
        self.loader.mysql.execute_update(
            """
INSERT INTO post (id, title, author, body, toc, path, date, updated, summary, category)
VALUES 
  ('1', 'First Post', 'John Doe', 'This is the content of the first post.', 'Table of Contents for the first post', '/path/to/first-post', '2023-10-24', '2023-10-24', 'Summary of the first post', 'News'),
  ('2', 'Second Post', 'Jane Smith', 'This is the content of the second post.', 'Table of Contents for the second post', '/path/to/second-post', '2023-10-25', '2023-10-25', 'Summary of the second post', 'Tutorial'),
  ('3', 'Third Post', 'Mike Johnson', 'This is the content of the third post.', 'Table of Contents for the third post', '/path/to/third-post', '2023-10-26', '2023-10-26', 'Summary of the third post', 'Technology');
"""
        )

    def tearDown(self) -> None:
        self.loader.mysql.execute_update("DROP DATABASE IF EXISTS test_db_postloader")

    def test_data(self):
        self.loader.set("1")

        data = self.loader.data

        expect_result = {
            "id": "1",
            "title": "First Post",
            "author": "John Doe",
            "body": "This is the content of the first post.",
            "toc": "Table of Contents for the first post",
            "path": "/path/to/first-post",
            "date": date(2023, 10, 24),
            "updated": date(2023, 10, 24),
            "summary": "Summary of the first post",
            "category": "News",
        }

        self.assertEqual(data["date"], expect_result["date"])
        self.assertEqual(data["newer"].data["title"], "Second Post")

    def test_recent(self):
        expect_result = {
            "id": "1",
            "title": "First Post",
            "author": "John Doe",
            "body": "This is the content of the first post.",
            "toc": "Table of Contents for the first post",
            "path": "/path/to/first-post",
            "date": date(2023, 10, 26),
            "updated": date(2023, 10, 26),
            "summary": "Summary of the first post",
            "category": "News",
        }
        data = self.loader.recent(1)[0]
        self.assertEqual(data["date"], expect_result["date"])


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
        time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.loader.mysql.execute_update(
            """
INSERT INTO
  trend (id, title, body, time, project, author_name, author_email)
VALUES
(1, '你好世界', '你好你好世界你好世界你好世界', '%s', '项目名称', '高天驰', '6159984@gmail.com')
"""
            % time
        )

    def tearDown(self) -> None:
        self.loader.mysql.execute_update("DROP DATABASE IF EXISTS test_db_trendloader")

    def test_data(self):
        self.loader.set(1)
        data = self.loader.data[0]
        self.assertEqual(data["title"], "你好世界")
        self.assertEqual(data["body"], "你好你好世界你好世界你好世界")
        self.assertTrue(isinstance(data["time"], datetime))

    def test_recent(self):
        data = self.loader.recent(1)[0]
        self.assertEqual(data["title"], "你好世界")
        self.assertEqual(data["body"], "你好你好世界你好世界你好世界")
        self.assertTrue(isinstance(data["time"], datetime))


class ProfileLoaderTestCase(unittest.TestCase):
    def setUp(self) -> None:
        app = Flask(__name__)
        app.config.from_object(config["base"])
        self.loader = ProfileLoader(app)

    def test_valid_profile(self):
        path = "D:\\dev\\repo\\myblog\\test\\example_file\\profile.json"
        self.loader.path = path

        data = self.loader.data

        self.assertEqual(data["author"]["name"], "高天驰")
        self.assertEqual(data["author"]["email"], "6159984@gmail.com")
        self.assertEqual(data["website"]["title"], "高天驰的个人博客")
        self.assertEqual(data["website"]["building_time"], "2023-10-24")
        self.assertEqual(
            data["website"]["description"],
            "本站专注于记录作者的编程学习过程，以具体的项目为驱动，不求完美，希望能让自己的编程技能达到实习水平。",
        )
        self.assertEqual(data["content"]["trend_repo"], ["D:\\dev\\data\\myblog\\ws2"])
