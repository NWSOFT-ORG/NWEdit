import tkinter as tk
from tkinter import ttk

from src.Utils.color_utils import lighten_color


class Entry(ttk.Frame):
    def __init__(self, master: tk.Misc):
        super().__init__(master)
        style = ttk.Style()
        self.bg = bg = style.lookup("TLabel", "background")
        self.fg = fg = style.lookup("TLabel", "foreground")

        self.entry = tk.Entry(
            self,
            bg=bg,
            fg=fg,
            insertbackground=fg,
            insertwidth=3,
            highlightthickness=0,
            bd=0,
        )
        self.entry.pack(fill="x", expand=True)
        self.entry.focus_set()
        self.entry.bind("<FocusIn>", self.entry_on_focus)
        self.entry.bind("<FocusOut>", self.entry_on_focus_out)

        self.border = tk.Canvas(
            self, height=2, takefocus=False, bg=fg, highlightthickness=0
        )
        self.border.pack(fill="x", expand=True, side="bottom")

    @property
    def widget_width(self):
        self.update()
        return self.winfo_width()

    def entry_on_focus(self, _):
        self.border.config(bg=self.fg)

    def entry_on_focus_out(self, _):
        darker_bg = lighten_color(self.bg, 40)
        self.border.config(bg=darker_bg)

    def get(self):
        return self.entry.get()

    def insert(self, pos: str = "end", text: str = ""):
        self.entry.insert(pos, text)
