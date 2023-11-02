"""
Abstract: This module defines commonly used auxiliary functions.

Author: Gao Tianchi
Contact: 6159984@gmail.com
Version: 0.3
Creation date: 2023-11-02
Latest modified date: 2023-11-02
Copyright (C) 2023 Gao Tianchi
"""

import base64
import hashlib
from datetime import date, datetime


def serialize_datetime(obj):
    if isinstance(obj, (date, datetime)):
        return obj.isoformat()
    raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")


def get_post_id(post_title: str) -> str:
    hash_object = hashlib.md5(post_title.encode())
    hash_digest = hash_object.digest()

    title_id = base64.urlsafe_b64encode(hash_digest)[:20].decode()

    return title_id
