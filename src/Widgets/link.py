from typing import *

from src.constants import OSX
from src.modules import tk, ttk
from src.Utils.color_utils import is_dark_color


class Link(ttk.Label):
    def __init__(self, parent: tk.Misc, text: Text, image: Union[tk.PhotoImage, None] = None):
        style = ttk.Style(parent)
        bg = style.lookup("TLabel", "background")
        fg = "#8dd9f7" if is_dark_color(bg) else "#499CD5"
        super().__init__(parent, cursor=self.cursor, foreground=fg,
        text=text, image=image, compound="left")

    @property
    def cursor(self):
        return "pointinghand" if OSX else "hand2"
