"""
职责：数据处理中心
"""


import pymysql


class MySQLHandler:
    """
    职责：操作 mysql 数据库
    """

    def __init__(self, host, user, password, database):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.connection = None
        self.cursor = None

    def __create_database(self) -> None:
        connection = pymysql.connect(
            host=self.host, user=self.user, password=self.password
        )
        cursor = connection.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.database}")
        connection.commit()
        cursor.close()
        connection.close()

    def connect(self):
        self.__create_database()

        self.connection = pymysql.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            database=self.database,
        )
        self.cursor = self.connection.cursor()

    def execute_query(self, query):
        self.cursor.execute(query)
        result = self.cursor.fetchall()
        return result

    def execute_update(self, query):
        self.cursor.execute(query)
        self.connection.commit()

    def close(self):
        self.cursor.close()
        self.connection.close()
