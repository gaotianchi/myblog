import json

from flask import Blueprint, current_app, request

from myblog.model.item import LogTimeLine, Profile

api = Blueprint("api", __name__)


@api.route("/trend")
def get_trend():
    before = request.args.get("before")

    profile = Profile(current_app)

    log_timeline_hanlder = LogTimeLine(
        current_app, profile.data["gitrepo"], before=before, count=10
    )

    logs = log_timeline_hanlder.logs

    return json.dumps(logs, ensure_ascii=False)
