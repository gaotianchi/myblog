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
        if path.is_file():
            self.content = path.read_text(encoding="utf-8").strip()
        else:
            self.content = ""

    def is_post(self) -> bool:
        if not self.path.is_file():
            logger.debug(f"{self.path} is not a file.")
            return False

        if not self.path.suffix == self.FILE_SUFFIX:
            logger.debug(
                f"The format of file {self.path.name} is not {self.FILE_SUFFIX}."
            )
            return False

        if not self.path.is_relative_to(self.PATH_ROOT):
            logger.debug(f"File {self.path.name} is not relative to post root dir.")
            return False

        logger.debug(f"File {self.path} is a post.")

        return True

    def get_metadata(self) -> dict:
        pattern = re.compile(r"---\n(.*?)\n---", re.DOTALL)
        match = pattern.match(self.content)

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
        pattern = re.compile(r"---.*?---", re.DOTALL)
        body: str = re.sub(pattern, "", self.content).strip()

        return body

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

        if cagegory_in_metadata:
            return cagegory_in_metadata

        if not self.path.parent is self.PATH_ROOT:
            return self.path.parent.stem

        return self.CATEGORY_DEFAULT_NAME

    def __repr__(self) -> str:
        return f"<Post {self.path.stem}>"


if __name__ == "__main__":
    ...
