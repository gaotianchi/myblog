import os
import shutil

from dotenv import load_dotenv

load_dotenv()

basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))


class BaseConfig:
    SECRET_KEY = os.getenv("SECRET_KEY")
    USERDATA_DIR = os.getenv("USERDATA_DIR")
    PROFILE_REQUIRE_ELEMENTS = os.getenv("PROFILE_REQUIRE_ELEMENTS")
    USER_DEFAULT_DIR = os.path.join(basedir, "default")
    LOG_DIR = os.path.join(basedir, "log")
    POSTSPACE = os.path.join(USERDATA_DIR, "文章")

    for path in [LOG_DIR, USERDATA_DIR]:
        if not os.path.exists(path):
            os.makedirs(path, exist_ok=True)

    for i in os.listdir(USER_DEFAULT_DIR):
        src = os.path.join(USER_DEFAULT_DIR, i)
        shutil.move(src, USERDATA_DIR)


class DevelopmentConfig(BaseConfig):
    SERVER_NAME = os.getenv("DEV_SERVER_NAME", "127.0.0.1:5000")


class ProductionConfig(BaseConfig):
    SERVER_NAME = os.getenv("PROD_SERVER_NAME")


config = {"dev": DevelopmentConfig, "prod": ProductionConfig}
