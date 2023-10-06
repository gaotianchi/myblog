import base64
import hashlib


def generate_id(title: str) -> str:
    hash_object = hashlib.md5(title.encode())
    hash_digest = hash_object.digest()

    title_id = base64.urlsafe_b64encode(hash_digest)[:7].decode()

    return title_id
