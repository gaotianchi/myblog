"""
职责：提供独立函数帮助
"""

import base64
import hashlib
import re

import yaml


def generate_id(title: str) -> str:
    hash_object = hashlib.md5(title.encode())
    hash_digest = hash_object.digest()

    title_id = base64.urlsafe_b64encode(hash_digest)[:10].decode()

    return title_id


def get_meta_and_body(md_text: str) -> dict:
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
