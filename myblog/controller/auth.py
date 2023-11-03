"""
Abstract: This module is used to define methods for authenticating users.

Required: 
    1. myblog.flaskexten
    2. myblog.model.database

Author: Gao Tianchi
Contact: 6159984@gmail.com
Version: 0.3
Creation date: 2023-11-03
Latest modified date: 2023-11-03
Copyright (C) 2023 Gao Tianchi
"""


from flask import current_app
from flask.wrappers import Request
from itsdangerous import BadSignature, Serializer, SignatureExpired

from myblog.flaskexten import login_manager
from myblog.model.database.db import Owner


def generate_token(owner: Owner):
    expiration = current_app.config["TOKEN_EXPRIATION"]
    s = Serializer(current_app.config["SECRET_KEY"], expires_in=expiration)
    token = s.dumps({"name": owner.name}).decode("ascii")
    return token, expiration


def get_user_from_token(token: str):
    s = Serializer(current_app.config["SECRET_KEY"])
    try:
        data = s.loads(token)

    except (BadSignature, SignatureExpired):
        return None  # Return None on token validation failure
    user = Owner.query.get(data["name"])
    return user  # Return the user object on successful validation


@login_manager.request_loader
def load_user_from_request(request: Request):
    # First, try to login using the token from the URL arg
    token = request.args.get("token")
    if token:
        user = get_user_from_token(token)
        if user:
            return user

    # Next, try to login using Basic Auth
    token = request.headers.get("Authorization")
    if token:
        token = token.replace("Basic ", "", 1)
        user = get_user_from_token(token)
        if user:
            return user

    # Finally, return None if both methods did not log in the user
    return None
