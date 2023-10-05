import os

from flask import Blueprint, current_app, jsonify, render_template

from myblog.model.processer import WritingSpaceReader

user = Blueprint("user", __name__)


@user.route("/")
def home():
    return render_template("home.html")


@user.route("/writingspace")
def writingconfig():
    reader = WritingSpaceReader(current_app)
    part: str = reader.data["path"]["homePostPath"]
    p = part.split("/")
    path = os.path.join(current_app.config["DATA_DIR"], *p)

    return path
