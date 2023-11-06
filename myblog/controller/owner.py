"""
Abstract: This module defines the owner's view function

Author: Gao Tianchi
Contact: 6159984@gmail.com
Version: 0.3
Creation date: 2023-11-03
Copyright (C) 2023 Gao Tianchi
"""

import json
import logging

from cryptography.fernet import Fernet
from flask import Blueprint, abort, current_app, g, request

from myblog.model.database.db import Owner

owner_bp = Blueprint("owner", __name__)


logger = logging.getLogger("controller")


def decrypt_token(secret_key: bytes, token: str) -> str:
    fernet = Fernet(secret_key)
    decrypted_data = fernet.decrypt(token.encode("utf-8"))

    return decrypted_data.decode("utf-8")


@owner_bp.before_request
def load_user():
    token: str = request.args.get("token")
    if token:
        try:
            decrypted_data: str = decrypt_token(current_app.config["SECRET_KEY"], token)
            data: dict = json.loads(decrypted_data)
            owner = Owner.query.get(data["name"])
            g.owner = owner

            logger.info(f"Login successfully.")
        except:
            logger.info(f"Fail to Login!")
            abort(401)

    return None
