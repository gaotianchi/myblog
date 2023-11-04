"""
Abstract: This module is used to define methods for authenticating users.

Required: 
    1. myblog.flaskexten
    2. myblog.model.database

Author: Gao Tianchi
Contact: 6159984@gmail.com
Version: 0.3
Creation date: 2023-11-03
Copyright (C) 2023 Gao Tianchi
"""

import json

from cryptography.fernet import Fernet
from flask import Blueprint, current_app
from flask.wrappers import Request
from flask_login import current_user, login_required

from myblog.flaskexten import login_manager
from myblog.model.database.db import Owner

auth_bp = Blueprint("auth", __name__)

login_manager.login_view = "auth.login"


def decrypt_token(secret_key: bytes, token: str) -> str:
    fernet = Fernet(secret_key)
    decrypted_data = fernet.decrypt(token.encode("utf-8"))

    return decrypted_data.decode("utf-8")


@login_manager.request_loader
def load_user_from_request(request: Request):
    token: str = request.args.get("token")
    if token:
        try:
            decrypted_data: str = decrypt_token(current_app.config["SECRET_KEY"], token)
            data: dict = json.loads(decrypted_data)
            owner = Owner.query.get(data["name"])
            return owner if owner else None
        except:
            return None

    return None


@auth_bp.route("/login")
def login():
    return "login"


@auth_bp.route("/")
@login_required
def index():
    return f"当前的用户名称为 {current_user.name}"
