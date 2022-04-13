from color_utils import is_dark_color
from src.modules import tk, ttk
from src.constants import OSX


class Link(ttk.Label):
    def __init__(self, parent: tk.Misc):
        style = ttk.Style(self)
        bg = style.lookup("TLabel", "backgroundd")
        fg = "#8dd9f7" if is_dark_color(bg) else "#499CD5"
        super().__init__(parent, cursor=self.cursor, foreground=fg)

    @property
    def cursor(self):
        return "pointinghand" if OSX else "hand2"
