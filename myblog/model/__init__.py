"""
职责：数据处理中心
"""


import pymysql
import redis
from redis import ConnectionPool


class RedisHandler:
    """
    职责：操作 redis 数据库
    """

    def __init__(self, host, port, password=None, db=0, max_connections=10):
        self.host = host
        self.port = port
        self.password = password
        self.db = db
        self.pool = self.__create_pool(max_connections)
        self.redis = self.__connect()

    def __create_pool(self, max_connections):
        return ConnectionPool(
            host=self.host,
            port=self.port,
            password=self.password,
            db=self.db,
            max_connections=max_connections,
        )

    def __connect(self):
        return redis.Redis(connection_pool=self.pool)

    def set(self, key, value):
        self.redis.set(key, value)

    def get(self, key) -> bytes:
        return self.redis.get(key)

    def delete(self, key):
        self.redis.delete(key)


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
