import tkinter as tk
from tkinter import ttk
from typing import Callable, Union

from constants import HAND_CURSOR
from src.Utils.color_utils import is_dark_color
from src.Utils.photoimage import PhotoImage


class Link(ttk.Label):
    def __init__(
        self, parent: tk.Misc, text: str, image: Union[PhotoImage, None] = None, command: Callable = lambda: None
    ):
        style = ttk.Style(parent)
        bg = style.lookup("TLabel", "background")
        fg = "#00BBFF" if is_dark_color(bg) else "#0077FF"
        super().__init__(
            parent,
            cursor=HAND_CURSOR,
            foreground=fg,
            text=text,
            image=image,
            compound="left",
        )
        self.bind("<1>", command, add=True)
