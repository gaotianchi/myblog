from flask import Blueprint, current_app

api = Blueprint("api", __name__)


@api.route("/")
def root():
    current_app.logger.info("请求根链接")
    return "hello world"


@api.route("/post")
def post():
    return "post"


@api.route("/image/<image_name>")
def image(image_name):
    return image_name
