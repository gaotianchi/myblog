"""
Created: 2023-11-21
Author: Gao Tianchi
"""


from markdown import Markdown

from myblog.definition import DefinePost


class Post:
    def __init__(self) -> None:
        self.toc = None

    def __call__(self, post: DefinePost) -> DefinePost:
        post.body = self.__convert(post.md_body)
        post.toc = self.toc

        return post

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


class Comment:
    def __call__(self, comment_content: str) -> str:
        html_content = self.__convert(comment_content)

        return html_content

    def __convert(self, md_text: str) -> str:
        md = Markdown()

        html_text = md.convert(md_text)
        return html_text


def get_render(name: str):
    match name:
        case "post":
            return Post()
        case "comment":
            return Comment()
