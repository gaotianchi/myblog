"""
Abstract: This module defines commonly used auxiliary functions.

Author: Gao Tianchi
Contact: 6159984@gmail.com
Version: 0.3
Creation date: 2023-11-02
Copyright (C) 2023 Gao Tianchi
"""

import base64
import hashlib
import logging
import re
from datetime import date, datetime

import yaml
from cryptography.fernet import Fernet

logger = logging.getLogger()


def serialize_datetime(obj):
    if isinstance(obj, (date, datetime)):
        return obj.isoformat()
    raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")


def get_post_id(post_title: str) -> str:
    hash_object = hashlib.md5(post_title.encode())
    hash_digest = hash_object.digest()

    title_id = base64.urlsafe_b64encode(hash_digest)[:20].decode()

    return title_id


def get_post_items(md_text: str) -> dict:
    data = {"metadata": {}, "body": ""}
    pattern = r"---\n(.*?)\n---"
    match = re.search(pattern, md_text, re.DOTALL)
    if match:
        yaml_text = match.group(1)
        try:
            metadata: dict = yaml.safe_load(yaml_text)
            data["metadata"] = metadata
        except:
            logger.warning(f"Fail to get post metadata.")

    body_text = re.sub(pattern, "", md_text, re.DOTALL)
    data["body"] = body_text

    return data


def encrypt_token(secret_key: bytes, data: str) -> str:
    fernet = Fernet(secret_key)
    token = fernet.encrypt(data.encode("utf-8"))

    return token.decode("utf-8")
