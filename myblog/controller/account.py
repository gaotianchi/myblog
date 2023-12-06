"""
Summary: Define view functions regarding account changes.
Created at: 2023-12-06
Author: Gao Tianchi
"""


import json

from flask import Blueprint, abort, jsonify, request, url_for

from myblog.email import send_email
from myblog.model.database import User

from .auth import decrypt_data, encrypt_data

account = Blueprint("account", __name__)


@account.route("/delete/account/<id>", methods=["DELETE"])
def delete_account(id: int):
    user = User.query.get(id)
    # Verify and confirm.
    user.delete()
    return jsonify("Deleted account."), 200


@account.route("/update/email/<id>", methods=["PATCH", "GET"])
def update_email(id: int):
    user = User.query.get(id)

    # Validate new email.
    if request.form:
        new_email = request.form.get("email")
        data = json.dumps(dict(new_email=new_email))
        token = encrypt_data(data)
        url = url_for(".update_email", id=user.id, token=token, _external=True)
        send_email(subject="Reset email.", recipients=[new_email], body=url)
        return jsonify(f"Check your new mail {new_email}"), 303

    token = request.args.get("token")
    if token:
        # Validate token.
        decrypted_data = json.loads(decrypt_data(token))
        new_email = decrypted_data["new_email"]
        user.update_email(new_email)
        return jsonify("Changed email."), 200

    return abort(400)


@account.route("/update/information/<id>", methods=["PATCH"])
def update_information(id):
    user = User.query.get(id)
    if request.form:
        form = request.form
        new_name = form.get("name")
        new_username = form.get("username")
        new_timezone = form.get("timezone")
        new_intro = form.get("intro")
        new_detail = form.get("detail")
        user.update_information(
            new_name, new_username, new_timezone, new_intro, new_detail
        )

        return jsonify(user.name), 200

    return abort(400)


@account.route("/update/password/<id>", methods=["PATCH"])
def update_password(id: int):
    user = User.query.get(id)
    if request.form:
        new_password = request.form.get("new_password")
        user.update_password(new_password)
        return jsonify("Changed password."), 200

    return abort(400)


@account.route("/sign/in", methods=["POST"])
def sign_in():
    if request.form:
        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(email=email).first()

        if not user:
            return jsonify("No account was found."), 403

        # Validate the form information.
        if not user.validate_password(password):
            return jsonify("Password was invalid."), 401

        return jsonify(f"Successfully log in. Welcome {user.name}."), 200

    return abort(401)


@account.route("/sign/up", methods=["POST", "GET"])
def sign_up():
    if request.form:
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")

        data = json.dumps(dict(name=name, email=email, password=password))
        token = encrypt_data(data)

        url = url_for("account.sign_up", token=token, _external=True)

        send_email("Validate email", [email], body=url)

        return jsonify(f"Check the mail {email}"), 303

    token = request.args.get("token")
    if token:
        # Validate token and get user information from token.

        decrypted_data = json.loads(decrypt_data(token))

        name = decrypted_data["name"]
        email = decrypted_data["email"]
        password = decrypted_data["password"]

        new_user = User.create(name, email, password)

        return jsonify(f"Successfully create new user {new_user.name}"), 201

    return abort(404)
