"""
Created at: 2023-12-06
Author: Gao Tianchi
"""

import base64


def encrypt_data(data: str):
    encoded_bytes = base64.b64encode(data.encode("utf-8"))
    encrypted_data = encoded_bytes.decode("utf-8")
    return encrypted_data


def decrypt_data(encrypted_data: str):
    encoded_bytes = encrypted_data.encode("utf-8")
    decoded_bytes = base64.b64decode(encoded_bytes)
    decrypted_data = decoded_bytes.decode("utf-8")
    return decrypted_data
