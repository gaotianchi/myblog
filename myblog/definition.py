"""
Created: 2023-11-20
Author: Gao Tianchi
"""

import logging
import re
import urllib.parse
from pathlib import Path

import yaml

from myblog.config import get_config

config = get_config()
logger = logging.getLogger("root")


def unsanitize_filename(encoded_filename):
    decoded_filename = urllib.parse.unquote(encoded_filename)
    return decoded_filename


class Owner:
    NAME: str = "Gao Tianchi"
    PATH_GITDIR: Path = config.PATH_ROOT.parent.joinpath("ws.git")
    PATH_WORKTREE: Path = config.PATH_ROOT.parent.joinpath("ws")


class Post:
    PATH_ROOT: Path = Owner.PATH_WORKTREE.joinpath("post")
    FILE_SUFFIX: str = ".md"
    CATEGORY_MAX_LENGTH: int = 255
    TITLE_MAX_LENGTH: int = 255
    AUTHOR_MAX_LENGTH: int = 255
    CATEGORY_DEFAULT_NAME: str = "Uncategorized"
    AUTHOR_DEFAULT_NAME: str = Owner.NAME

    AUTHOR_KEY_NAME: str = "author"
    CATEGORY_KEY_NAME: str = "category"

    def __init__(self, path: Path) -> None:
        self.path = path

    def is_post(self) -> bool:
        if not self.path.suffix == self.FILE_SUFFIX:
            logger.debug(
                f"The format of file {self.path.name} is not {self.FILE_SUFFIX}."
            )
            return False

        if not self.path.is_relative_to(self.PATH_ROOT):
            logger.debug(f"File {self.path.name} is not relative to post root dir.")
            return False

        content: str = self.path.read_text(encoding="utf-8").strip()
        pattern = re.compile(r"---.*?---", re.DOTALL)
        body: str = re.sub(pattern, "", content).strip()

        if not body:
            logger.debug(
                f"The article text cannot be empty, file {self.path} is not a post."
            )
            return False
        else:
            self.__body = body

        logger.debug(f"File {self.path} is a post.")

        return True

    def get_metadata(self) -> dict:
        content: str = self.path.read_text(encoding="utf-8").strip()
        pattern = re.compile(r"---\n(.*?)\n---", re.DOTALL)
        match = pattern.match(content)

        if not match:
            logger.debug(f"There is no metadata in post {self.path}.")
            return {}

        yaml_content: str = match.group(1)
        if not yaml_content:
            logger.warning(f"Post {self.path} has empty yaml filed.")
            return {}

        try:
            metadata: dict = yaml.load(yaml_content, Loader=yaml.SafeLoader)
        except yaml.error.MarkedYAMLError as e:
            logger.error(f"Fail to load yaml content with error code {e.problem}.")
            return {}
        else:
            if not metadata:
                logger.warning(f"Post {self.path} has empty yaml filed.")
                return {}

            return metadata

    def delete(self) -> None:
        self.path.unlink()

    @property
    def TITLE(self) -> str:
        return unsanitize_filename(self.path.stem)

    @property
    def BODY(self) -> str:
        return self.__body

    @property
    def AUTHOR(self) -> str:
        metadata: dict = self.get_metadata()
        if not metadata:
            return self.AUTHOR_DEFAULT_NAME
        if metadata.get(self.AUTHOR_KEY_NAME):
            return metadata.get(self.AUTHOR_KEY_NAME)

    @property
    def CATEGORY(self) -> str:
        metadata: dict = self.get_metadata()

        cagegory_in_metadata: str | None = metadata.get(self.CATEGORY_KEY_NAME)

        def valid_length(category_name: str) -> bool:
            result = len(category_name) <= self.CATEGORY_MAX_LENGTH
            if not result:
                logger.warning(
                    f"The length of category name {category_name} is more then max length {self.CATEGORY_MAX_LENGTH}!"
                )
            return result

        if cagegory_in_metadata and valid_length(cagegory_in_metadata):
            return cagegory_in_metadata
        else:
            logger.warning(
                f"Category name {cagegory_in_metadata} in the metadata is invalid!"
            )

        if (
            valid_length(self.path.parent.name)
            and self.path.parent.name is not self.PATH_ROOT
        ):
            return self.path.parent.name
        else:
            logger.warning(
                f"Category name {self.path.parent.name} with dirname is invalid!"
            )

        logger.debug(f"Finally using default category name as category name.")

        return self.CATEGORY_DEFAULT_NAME

    def __repr__(self) -> str:
        return f"<Post {self.path.stem}>"


if __name__ == "__main__":
    ...
