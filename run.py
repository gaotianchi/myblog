import os

from dotenv import load_dotenv

from myblog import create_app
from myblog.model.scheduler import Scheduler

load_dotenv()


config_name = os.getenv("CONFIG", "development")
app = create_app(config_name)


if __name__ == "__main__":
    app.run(debug=True)
