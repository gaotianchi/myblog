"""
职责：加载 flask 拓展
"""
from flask.wrappers import Request
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
login_manager = LoginManager()


@login_manager.request_loader
def load_user_from_request(request: Request):
    """
    职责：从请求体中加载作者对象
    """
    ...
