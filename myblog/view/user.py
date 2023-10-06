from flask import Blueprint, render_template

user = Blueprint("user", __name__)


@user.route("/")
def home():
    return render_template("base.html")
