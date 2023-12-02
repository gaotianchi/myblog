"""
Created: 2023-12-01
Author: Gao Tianchi
"""


import re
from collections import defaultdict

from cryptography.fernet import Fernet


def title_to_url(title: str) -> str:
    url_title = title.replace(" ", "-")
    url_title = re.sub(r"[^a-zA-Z0-9\-]", "", url_title)
    return url_title


def generate_token(key: bytes, data: bytes) -> bytes:
    # Generate owner's token.

    f = Fernet(key)
    token: bytes = f.encrypt(data)

    return token


def archive_post_by_date(posts: list) -> dict:
    archive = defaultdict(dict)

    for post in posts:
        year = post.created.year
        month = post.created.month

        month_posts = archive[year].get(month, [])
        month_posts.append(post)
        archive[year][month] = month_posts

    return archive