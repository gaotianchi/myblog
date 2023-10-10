import os

from dotenv import load_dotenv

from myblog import create_app

load_dotenv()


config_name = os.getenv("CONFIG", "dev")
app = create_app(config_name)
