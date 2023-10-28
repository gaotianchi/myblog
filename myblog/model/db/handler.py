"""
职责：定义数据库操作句柄
"""

import pymysql


class MySQLHandler:
    """
    职责：操作 mysql 数据库
    """

    def __init__(self, host, user, password, database) -> None:
        self.connection = pymysql.connect(
            host=host, user=user, password=password, database=None
        )
        self.cursor = self.connection.cursor()
        self.database = database

        if database:
            self.create_database_if_not_exists(database)
            self.connection.select_db(database)

    def create_database_if_not_exists(self, database):
        create_database_query = f"CREATE DATABASE IF NOT EXISTS {database}"
        self.cursor.execute(create_database_query)

    def get(self, query) -> tuple[tuple]:
        self.cursor.execute(query)
        result = self.cursor.fetchall()
        return result

    def modify(self, query) -> None:
        self.cursor.execute(query)
        self.connection.commit()

    def close(self) -> None:
        self.cursor.close()
        self.connection.close()
