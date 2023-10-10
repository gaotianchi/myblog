import os

from dotenv import load_dotenv

load_dotenv()

basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))


class BaseConfig:
    # 环境变量
    SECRET_KEY = os.getenv("SECRET_KEY")

    # 配置默认路径
    LOG_DIR = os.path.join(basedir, "logs")
    DATA_DIR = os.path.join(basedir, "data")

    POSTSPACE = os.path.join(DATA_DIR, "文章")
    WRITINGSPACE = os.path.join(DATA_DIR, "writingspace.json")

    for path in [LOG_DIR, DATA_DIR]:
        if not os.path.exists(path):
            os.makedirs(path, exist_ok=True)


class DevelopmentConfig(BaseConfig):
    SERVER_NAME = os.getenv("DEV_SERVER_NAME", "127.0.0.1:5000")


class ProductionConfig(BaseConfig):
    SERVER_NAME = os.getenv("PROD_SERVER_NAME")


config = {"dev": DevelopmentConfig, "prod": ProductionConfig}
