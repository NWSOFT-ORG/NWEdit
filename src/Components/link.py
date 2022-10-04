import tkinter as tk
from tkinter import ttk
from typing import Callable, Union

from src.constants import OSX
from src.Utils.color_utils import is_dark_color
from src.Utils.photoimage import PhotoImage


class Link(ttk.Label):
    def __init__(
        self, parent: tk.Misc, text: str, image: Union[PhotoImage, None] = None, command: Callable = lambda: None
    ):
        style = ttk.Style(parent)
        bg = style.lookup("TLabel", "background")
        fg = "#8dd9f7" if is_dark_color(bg) else "#499CD5"
        super().__init__(
            parent,
            cursor=self.cursor,
            foreground=fg,
            text=text,
            image=image,
            compound="left",
        )
        self.bind("<1>", command, add=True)

    @property
    def cursor(self):
        return "pointinghand" if OSX else "hand2"
