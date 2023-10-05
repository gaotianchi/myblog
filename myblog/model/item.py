import redis
from model import pool

conn = redis.Redis(connection_pool=pool)


class Post:
    def __init__(self) -> None:
        pass


class WritingSpace:
    pass
