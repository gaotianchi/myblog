"""
Abstract: This module defines the rendering method for specific data types.

Author: Gao Tianchi
Contact: 6159984@gmail.com
Version: 0.3
Creation date: 2023-11-05
Copyright (C) 2023 Gao Tianchi
"""

from .render import Render


class PostRender:
    def __init__(self) -> None:
        self.render = Render()
