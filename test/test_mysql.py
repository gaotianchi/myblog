import datetime
import unittest
from datetime import date

from flask import Flask

from myblog.model import MySQLHandler
from myblog.model.dbupdater import PostCleaner, PostDbUpdater
from myblog.model.item import PostLoader
from myblog.setting import config


class PostDbUpdaterAndPostCleanerTestCase(unittest.TestCase):
    def setUp(self):
        mysql_config = config["base"].MYSQL_CONFIG
        mysql_config["database"] = "test_db_1"
        app = Flask(__name__)
        app.config["MYSQL_HANDLER"] = MySQLHandler(**mysql_config)

        self.postdbupdater = PostDbUpdater(app)
        self.postcleaner = PostCleaner(app)

        self.postdbupdater.mysql.connect()

    def tearDown(self):
        self.postdbupdater.mysql.execute_update("DROP DATABASE IF EXISTS test_db_1")

        self.postdbupdater.mysql.close()

    def test_key_is_exist(self):
        self.postdbupdater.mysql.execute_update(
            """
INSERT INTO post (id, title, author, body, toc, path, date, updated, summary, category)
VALUES
  ('1', 'Title 1', 'Author 1', 'Body 1', 'Table of Contents 1', '/path/to/post1', '2023-01-01', '2023-01-02', 'Summary 1', 'Category 1'),
  ('2', 'Title 2', 'Author 2', 'Body 2', 'Table of Contents 2', '/path/to/post2', '2023-02-01', '2023-02-02', 'Summary 2', 'Category 2'),
  ('3', 'Title 3', 'Author 3', 'Body 3', 'Table of Contents 3', '/path/to/post3', '2023-03-01', '2023-03-02', 'Summary 3', 'Category 3');
"""
        )
        self.postdbupdater.metadata = {"id": "4"}
        result_1 = self.postdbupdater._PostDbUpdater__key_is_exist()
        self.assertFalse(result_1)

        self.postdbupdater.metadata = {"id": "1"}
        result_2 = self.postdbupdater._PostDbUpdater__key_is_exist()
        self.assertTrue(result_2)

    def test_update(self):
        self.postdbupdater.metadata = dict(
            id="1",
            title="Title 1",
            author="Author 1",
            path="/path/to/post1",
            date="2023-01-01",
            updated="2023-01-02",
            summary="Summary 1",
            category="Category 1",
        )
        self.postdbupdater.body_items = dict(body="Body 1", toc="Toc 1")
        self.postdbupdater.update()

        result = self.postdbupdater.mysql.execute_query(
            "SELECT date FROM post WHERE id='1';"
        )
        self.assertEqual(result[0][0], date(2023, 1, 1))

        self.postdbupdater.metadata["title"] = "Title 2"
        self.postdbupdater.update()

        result = self.postdbupdater.mysql.execute_query(
            "SELECT title FROM post WHERE id='1';"
        )

        self.assertEqual(result[0][0], "Title 2")

    def test_delete(self):
        self.postcleaner.set("1")
        self.postcleaner.delete()

        result = self.postdbupdater.mysql.execute_query(
            "SELECT id FROM post WHERE id='1';"
        )
        self.assertEqual(result, ())


class ItemLoaderTestCase(unittest.TestCase):
    def setUp(self):
        mysql_config = config["base"].MYSQL_CONFIG
        mysql_config["database"] = "test_db_2"
        app = Flask(__name__)
        app.config["MYSQL_HANDLER"] = MySQLHandler(**mysql_config)

        self.post_loader = PostLoader(app)
        self.post_loader.mysql.connect()

        self.post_loader.mysql.execute_update(
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

        self.post_loader.mysql.execute_update(
            """
INSERT INTO post (id, title, author, body, toc, path, date, updated, summary, category)
VALUES
  ('1', 'Title 1', 'Author 1', 'Body 1', 'Table of Contents 1', '/path/to/post1', '2023-01-01', '2023-01-02', 'Summary 1', 'Category 1'),
  ('2', 'Title 2', 'Author 2', 'Body 2', 'Table of Contents 2', '/path/to/post2', '2023-02-01', '2023-02-02', 'Summary 2', 'Category 2'),
  ('3', 'Title 3', 'Author 3', 'Body 3', 'Table of Contents 3', '/path/to/post3', '2023-03-01', '2023-03-02', 'Summary 3', 'Category 3');
"""
        )

    def tearDown(self):
        self.post_loader.mysql.execute_update("DROP DATABASE IF EXISTS test_db_2")

        self.post_loader.mysql.close()

    def test_data(self):
        self.post_loader.set(post_id="1")
        data = self.post_loader.data
        expect_result = dict(
            id="1",
            title="Title 1",
            author="Author 1",
            body="Body 1",
            toc="Table of Contents 1",
            path="/path/to/post1",
            date=datetime.date(2023, 1, 1),
            updated=datetime.date(2023, 1, 2),
            summary="Summary 1",
            category="Category 1",
        )

        self.assertEqual(data["date"], expect_result["date"])
        self.assertEqual(data["newer"].data["id"], "2")
        self.assertEqual(data["older"], None)


if __name__ == "__main__":
    unittest.main()
