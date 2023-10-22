import os

from flask import Blueprint, request, send_from_directory

api = Blueprint("api", __name__)


@api.route("/image")
def image():
    PATH_WORKTREE_USERDATA = os.getenv("PATH_WORKTREE_USERDATA", "")
    PATH_IMG = os.path.join(PATH_WORKTREE_USERDATA, "图片")

    name = request.args.get("name")

    if not os.path.exists(os.path.join(PATH_IMG, name)):
        return ""

    # TODO: 检验该文件的有效性

    return send_from_directory(PATH_IMG, name)
