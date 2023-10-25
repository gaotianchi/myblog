import datetime
import json
import os

from flask import Blueprint, current_app, request, send_from_directory

from myblog.model.itemloader import TrendLoader
from myblog.model.utlis import convert_datetime

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


@api.route("/trend")
def get_trend():
    """
    职责：给 js 端提供 trend 数据
    """
    count = int(
        request.args.get("count", current_app.config["HOME_RECENT_TREND_COUNT"])
    )
    start_id = int(request.args.get("start_id"))

    trend_ids = list(range(start_id, start_id - count, -1))

    trendloader = TrendLoader(current_app)
    trendloader.set(*trend_ids)

    data = trendloader.data

    return json.dumps(data, ensure_ascii=False, default=convert_datetime)
