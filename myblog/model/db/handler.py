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
            host=host, user=user, password=password, database=database
        )
        self.cursor = self.connection.cursor()

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
