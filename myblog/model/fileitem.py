"""
Created: 2023-12-02
Author: Gao Tianchi
"""


import json
import logging
import re
from datetime import date, datetime
from pathlib import Path

import yaml

from myblog.config import get_config

config = get_config()
logger = logging.getLogger("model.fileitem")


class OwnerProfile:
    GITDIR: Path = config.PATH_GITDIR
    WORKTREE: Path = config.PATH_WORKTREE

    def __init__(self) -> None:
        self.data = self.__read_profile()

    def __read_profile(self) -> dict:
        path_profile: Path = self.WORKTREE.joinpath("profile.json")

        if not path_profile.exists():
            return {}

        profile: dict = json.loads(path_profile.read_text(encoding="utf-8"))

        if not profile:
            return {}

        return profile

    @property
    def name(self) -> str:
        return self.data.get("name", "owner name")

    @property
    def email(self) -> str:
        return self.data.get("email", "owner email")

    @property
    def blog_title(self) -> str:
        website: dict = self.data.get("website", {})
        return website.get("blog_title", "blog title")

    @property
    def language(self) -> str:
        website: dict = self.data.get("website", {})
        return website.get("language", "en-us")

    @property
    def link(self) -> str:
        website: dict = self.data.get("website", {})
        return website.get("link", "http://example.com")

    @property
    def created_date(self) -> date:
        website: dict = self.data.get("website", {})
        d = website.get("created_date")
        if not d:
            d = date.today()
        d = datetime.strptime(d, "%Y-%m-%d").today()
        return d

    @property
    def description(self) -> str:
        website: dict = self.data.get("website", {})
        return website.get("description", "website description")


class PostFile:
    OWNER = OwnerProfile()

    PATH_ROOT: Path = OWNER.WORKTREE.joinpath("post")
    AUTHOR_DEFAULT_NAME: str = OWNER.name
    FILE_SUFFIX: str = ".md"
    CATEGORY_MAX_LENGTH: int = 255
    TITLE_MAX_LENGTH: int = 255
    AUTHOR_MAX_LENGTH: int = 255
    CATEGORY_DEFAULT_NAME: str = "Uncategorized"

    AUTHOR_KEY_NAME: str = "author"
    CATEGORY_KEY_NAME: str = "category"
    SUMMARY_KEY_NAME: str = "summary"

    def __init__(self, path: Path) -> None:
        self.path = path
        self.title = self.path.stem

        if self.is_post():
            self.content = self.path.read_text(encoding="utf-8")
            self.metadata = self.__read_metadata()
            self.body = self.__read_body()
            self.html = ""
            self.toc = None

    def is_post(self) -> bool:
        if not self.path.is_file():
            logger.error(f"{self.path} is not a file.")
            return False

        if not self.path.suffix == self.FILE_SUFFIX:
            logger.debug(
                f"The format of file {self.path.name} is not {self.FILE_SUFFIX}."
            )
            return False

        if not self.path.is_relative_to(self.PATH_ROOT):
            logger.debug(f"File {self.path.name} is not relative to post root dir.")
            return False

        return True

    def __read_metadata(self) -> dict:
        pattern = re.compile(r"---\n(.*?)\n---", re.DOTALL)
        match = pattern.match(self.content)

        if not match:
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

    def __read_body(self) -> str:
        pattern = re.compile(r"---.*?---", re.DOTALL)
        body: str = re.sub(pattern, "", self.content).strip()

        return body

    @property
    def author(self) -> str:
        if self.metadata.get(self.AUTHOR_KEY_NAME):
            return self.metadata.get(self.AUTHOR_KEY_NAME)

        return self.AUTHOR_DEFAULT_NAME

    @property
    def category(self) -> str:
        cagegory_in_metadata: str | None = self.metadata.get(self.CATEGORY_KEY_NAME)

        if cagegory_in_metadata:
            logger.debug(
                f"Using {cagegory_in_metadata} as category which is defined in the metadata."
            )
            return cagegory_in_metadata

        if self.path.parent.parent.is_relative_to(self.PATH_ROOT):
            logger.debug(f"Using dirname {self.path.parent.stem} as category name")
            return self.path.parent.stem

        logger.debug(f"Using default category name {self.CATEGORY_DEFAULT_NAME}")
        return self.CATEGORY_DEFAULT_NAME

    @property
    def summary(self) -> str:
        summary_in_metadata: str | None = self.metadata.get(self.SUMMARY_KEY_NAME)
        if summary_in_metadata:
            logger.debug(
                f"Using {summary_in_metadata[0:30]} as summary which difined in the metadata."
            )
            return summary_in_metadata

        md_without_title: str = re.sub(r"#+ .*?\n", "", self.body, re.DOTALL)
        md_without_title: str = re.sub(r"\n+", "\n", md_without_title, re.DOTALL)
        default_summary: str = md_without_title.split("\n")[0]

        return default_summary

    def __repr__(self) -> str:
        return f"<Post {self.path.stem}>"
