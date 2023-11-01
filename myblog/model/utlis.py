"""
职责：提供独立函数帮助
"""
import base64
import datetime
import hashlib
import json
import re

import yaml


def custom_slugify(value, separator):
    """自定义锚点链接"""

    value = re.sub(r"[^\w\s-]", "", value).strip().lower()
    return re.sub(r"[{}\s]+".format(separator), separator, value)


def generate_id(title: str) -> str:
    hash_object = hashlib.md5(title.encode())
    hash_digest = hash_object.digest()

    title_id = base64.urlsafe_b64encode(hash_digest)[:10].decode()

    return title_id


def get_meta_and_body(md_text: str) -> dict[str, str]:
    """
    职责：从 markdown 文档中获取 yaml 格式的元数据
    """
    pattern = r"---\n(.*?)\n---(.*)"
    match = re.search(pattern, md_text, re.DOTALL)
    data = {"metadata": {}, "body": ""}
    if match:
        yaml_text = match.group(1)
        body_text = match.group(2)
        try:
            data["metadata"]: dict = yaml.safe_load(yaml_text)
            data["body"]: str = body_text
        except:
            return data

    return data


def get_summary_and_body(git_message: str) -> dict:
    """
    职责：从 git 消息中分离出 summary 和 body
    按照约定，第一个换行符前的段落为 summary, 其余的为 body
    """

    items: list[str] = git_message.strip().split("\n", 1)

    if len(items) < 2:
        return {"summary": "", "body": ""}

    summary, body = items

    return dict(summary=summary.strip(), body=body.strip())


def get_data_from_json_file(path: str) -> dict:
    """
    职责：从 json 文件中读取数据
    """
    with open(path, "r", encoding="utf-8") as file:
        data = json.load(file)
    return data


def convert_datetime(obj):
    if isinstance(obj, datetime.datetime):
        return obj.strftime("%Y-%m-%d %H:%M")
    if isinstance(obj, datetime.date):
        return obj.strftime("%Y-%m-%d")
