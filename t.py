import base64
import hashlib
import json

import requests
from cryptography.fernet import Fernet

with open("KEY", "r", encoding="utf-8") as f:
    secret_key = f.read().encode("utf-8")


def get_post_id(post_title: str) -> str:
    hash_object = hashlib.md5(post_title.encode())
    hash_digest = hash_object.digest()

    title_id = base64.urlsafe_b64encode(hash_digest)[:20].decode()

    return title_id


def encrypt_token(secret_key: bytes, data: str) -> str:
    fernet = Fernet(secret_key)
    token = fernet.encrypt(data.encode("utf-8"))

    return token.decode("utf-8")


token = encrypt_token(secret_key, '{"name": "gaotianchi"}')

post_id: str = get_post_id("world world world")
url = f"http://localhost:5000/delete-post/{post_id}?token={token}"
json_data: str = json.dumps(
    dict(
        title="world world world",
        author="gaotianchi",
        body="hello hello hello",
        summary="hkkkkkk",
        category="hello",
    )
)


try:
    response = requests.delete(url)
    print(response.status_code)
except:
    print(response.status_code)
