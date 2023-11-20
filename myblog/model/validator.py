"""
Created: 2023-11-21
Author: Gao Tianchi
"""

import logging

from cryptography.fernet import Fernet

logger = logging.getLogger("model.validator")


def validate_token(token: bytes, key: bytes) -> bool:
    f = Fernet(key)
    try:
        decrypted_data: bytes = f.decrypt(token)
    except Exception as e:
        logger.error(f"Fail to get decrypted data with error message {e}")
        return False

    if decrypted_data == b"gaotianchi":
        logger.info("Token is valid.")
        return True
    else:
        logger.error("Token is invalid!")
        return False
