import json
from datetime import datetime, timedelta

from flask import Blueprint, current_app, request

from myblog.model.item import LogTimeLine, Profile

api = Blueprint("api", __name__)


@api.route("/trend")
def get_trend():
    b = request.args.get("before")
    current_app.logger.info(f"从视图函数接收到的 before 值为: {b}")
    before_datetime = datetime.strptime(b, "%Y-%m-%d")
    since_datetime = before_datetime - timedelta(days=3)
    before = before_datetime.date().isoformat()
    since = since_datetime.date().isoformat()

    profile = Profile(current_app)

    log_timeline_hanlder = LogTimeLine(
        current_app, profile.data["gitrepo"], before=before, since=since, count=100
    )

    logs = log_timeline_hanlder.logs
    current_app.logger.info(f"logs: {logs}")

    return json.dumps(logs, ensure_ascii=False)
