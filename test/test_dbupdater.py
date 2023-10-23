import unittest
from datetime import datetime

from flask import Flask

from myblog.model import MySQLHandler
from myblog.model.dbupdater import TrendDbUpdater
from myblog.setting import config


class TrendProcesserTestCase(unittest.TestCase):
    def setUp(self):
        mysql_config = config["base"].MYSQL_CONFIG
        mysql_config["database"] = "test_db_1"
        app = Flask(__name__)
        app.config["MYSQL_HANDLER"] = MySQLHandler(**mysql_config)

        self.trenddbupdater = TrendDbUpdater(app)
        self.trenddbupdater.mysql.connect()

    def tearDown(self):
        self.trenddbupdater.mysql.execute_update("DROP DATABASE IF EXISTS test_db_1")

        self.trenddbupdater.mysql.close()

    def test_update(self):
        trends = {
            "id": "1",
            "title": "Trend Title Trend Title",
            "body": "Trend Body Trend Body Trend Body Trend Body Trend Body Trend Body",
            "time": datetime.today().strftime("%Y-%m-%d %H:%M:%S"),
            "project": "Project A",
            "author_name": "John Doe",
            "author_email": "johndoe@example.com",
        }

        self.trenddbupdater.set(trends)
        self.trenddbupdater.update()

        result = self.trenddbupdater.mysql.execute_query(
            "SELECT * FROM trend WHERE id = '1'"
        )
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0][1], "Trend Title Trend Title")
        self.assertEqual(
            result[0][2],
            "Trend Body Trend Body Trend Body Trend Body Trend Body Trend Body",
        )
        self.assertTrue(result[0][3], datetime)
        self.assertEqual(result[0][4], "Project A")
        self.assertEqual(result[0][5], "John Doe")
        self.assertEqual(result[0][6], "johndoe@example.com")
