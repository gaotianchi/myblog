from dotenv import load_dotenv

from myblog import create_app

load_dotenv()


if __name__ == "__main__":
    app = create_app()
