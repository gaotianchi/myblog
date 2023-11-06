"""
Abstract: This module defines a renderer that converts markdown text into html text.

Author: Gao Tianchi
Contact: 6159984@gmail.com
Version: 0.3
Creation date: 2023-11-05
Copyright (C) 2023 Gao Tianchi
"""


from markdown import Markdown


class Render:
    ...

    def __init__(self) -> None:
        self.toc = None

    def __call__(self, md_text: str) -> str:
        return self.__convert(md_text)

    def __convert(self, md_text: str) -> str:
        md = Markdown(
            extensions=[
                "toc",
                "footnotes",
            ],
            extension_configs={
                "toc": {
                    "baselevel": 2,
                },
            },
        )

        html_text = md.convert(md_text)

        empty_toc = """
<div class="toc">
<ul></ul>
</div>
""".strip()

        if md.toc.strip() != empty_toc.strip():
            self.toc = md.toc

        return html_text
