import base64
import hashlib
from datetime import date, datetime

from cryptography.fernet import Fernet


def json_serial(obj):
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()


def generate_post_id(title: str) -> str:
    hash_object = hashlib.md5(title.encode())
    hash_digest = hash_object.digest()

    title_id = base64.urlsafe_b64encode(hash_digest)[:20].decode()

    return title_id


def decrypt_data(key: bytes, encrypted_data: bytes) -> str:
    """
    职责：解密数据
    """
    fernet = Fernet(key)
    decrypted_data = fernet.decrypt(encrypted_data)

    return decrypted_data.decode("utf-8")
