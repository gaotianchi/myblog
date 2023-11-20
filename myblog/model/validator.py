"""
Created: 2023-11-21
Author: Gao Tianchi
"""

import logging
from abc import ABC, abstractmethod

from cryptography.fernet import Fernet

logger = logging.getLogger("model.validator")


class Validator(ABC):
    @abstractmethod
    def set(self) -> None:
        ...

    @abstractmethod
    def validate(self) -> bool:
        ...


class Token(Validator):
    def set(self, token: bytes, key: bytes) -> None:
        self.token = token
        self.key = key

    def validate(self) -> bool:
        f = Fernet(self.key)
        try:
            decrypted_data: bytes = f.decrypt(self.token)
        except Exception as e:
            logger.error(f"Fail to get decrypted data with error message {e}")
            return False

        if decrypted_data == b"gaotianchi":
            logger.info("Token is valid.")
            return True
        else:
            logger.error("Token is invalid!")
            return False


def get_validator(name: str) -> Validator:
    match name:
        case "token":
            return Token()
