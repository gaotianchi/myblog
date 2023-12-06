"""
Created at: 2023-12-06
Author: Gao Tianchi
"""

import base64

from flask import Blueprint, g, jsonify, request, session

from myblog.model.database import User

auth = Blueprint("auth", __name__)


@auth.before_app_request
def load_author():
    if request.endpoint.startswith("author"):
        # Method 1: load user from session.
        if session.get("user_id"):
            user_id = session.get("user_id")
            user = User.query.get(user_id)
            if not user:
                return jsonify("Invalid user id."), 401
            g.user = user
            return None

        # Method 2: Basic auth.
        if request.authorization:
            email = request.authorization.get("username")
            password = request.authorization.get("password")

            user = User.query.filter_by(email=email).first()
            if not user:
                return jsonify("No user was found."), 401
            if not user.validate_password(password):
                return jsonify("Password was invalid."), 403
            g.user = user
            return None

        # Method 3: Api key.
        if request.headers.get("api"):
            api = request.headers.get("api")

            # Validate this api.
            ...


def encrypt_data(data: str):
    encoded_bytes = base64.b64encode(data.encode("utf-8"))
    encrypted_data = encoded_bytes.decode("utf-8")
    return encrypted_data


def decrypt_data(encrypted_data: str):
    encoded_bytes = encrypted_data.encode("utf-8")
    decoded_bytes = base64.b64decode(encoded_bytes)
    decrypted_data = decoded_bytes.decode("utf-8")
    return decrypted_data
