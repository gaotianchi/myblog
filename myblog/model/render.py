"""
Created: 2023-11-21
Author: Gao Tianchi
"""

from markdown import Markdown

from myblog.definition import Post as PostFile


class Render:
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


class Post:
    render = Render()

    def __call__(self, post: PostFile) -> PostFile:
        post.body = self.render(post.md_body)
        post.toc = self.render.toc

        return post


def get_render(name: str):
    match name:
        case "post":
            return Post()
