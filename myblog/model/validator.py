"""
Created: 2023-11-21
Author: Gao Tianchi
"""

import logging
from abc import ABC, abstractmethod

from cryptography.fernet import Fernet

from myblog.definition import Post as PostFile

logger = logging.getLogger("model.validator")


class Validator(ABC):
    @abstractmethod
    def set(self) -> None:
        ...

    @abstractmethod
    def validate(self) -> bool:
        ...

    @abstractmethod
    def get_message(self) -> list:
        ...


class Token(Validator):
    def __init__(self) -> None:
        self.messages: list[str] = []

    def set(self, token: bytes, key: bytes) -> None:
        self.token = token
        self.key = key

    def get_message(self) -> list:
        return self.messages

    def validate(self) -> bool:
        f = Fernet(self.key)
        try:
            decrypted_data: bytes = f.decrypt(self.token)
        except Exception as e:
            message = f"Fail to get decrypted data with error message {e}"
            self.messages.append(message)
            logger.error(message)
            return False

        if decrypted_data == b"gaotianchi":
            logger.info("Token is valid.")
            return True
        else:
            logger.error("Token is invalid!")
            return False


class Post(Validator):
    def __init__(self) -> None:
        self.messages: list[str] = []

    def set(self, post: PostFile) -> None:
        self.post = post

    def get_message(self):
        return self.messages

    def validate(self) -> bool:
        return (
            self.__validate_author()
            and self.__validate_body()
            and self.__validate_category()
            and self.__validate_title()
        )

    def __validate_title(self) -> bool:
        title: str = self.post.title
        max_length: int = self.post.TITLE_MAX_LENGTH

        if not len(title) <= max_length:
            message = f"The length of title of {self.post} is too long."
            self.messages.append(message)
            logger.error(message)
            return False

        return True

    def __validate_body(self) -> bool:
        body = self.post.body.strip()

        if not body:
            message = f"The body of {self.post} can not be empty."
            self.messages.append(message)
            logger.error(message)
            return False

        return True

    def __validate_author(self) -> bool:
        author = self.post.author
        max_length: int = self.post.AUTHOR_MAX_LENGTH

        if not len(author) <= max_length:
            message = f"The length of author of {self.post} is too long."
            self.messages.append(message)
            logger.error(message)
            return False

        return True

    def __validate_category(self) -> bool:
        category = self.post.category
        max_length: int = self.post.CATEGORY_MAX_LENGTH

        if not len(category) <= max_length:
            message = f"The length of category of {self.post} is too long."
            self.messages.append(message)
            logger.error(message)
            return False

        return True


def get_validator(name: str) -> Validator:
    match name:
        case "token":
            return Token()
        case "post":
            return Post()
