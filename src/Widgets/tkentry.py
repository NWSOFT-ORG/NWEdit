from src.modules import tk, ttk


class Entry(ttk.Frame):
    def __init__(self, parent: tk.Misc):
        super().__init__(parent)
        style = ttk.Style()
        self.bg = bg = style.lookup("TLabel", "background")
        self.fg = fg = style.lookup("TLabel", "foreground")

        self.entry = tk.Entry(self, bg=bg, fg=fg, insertbackground=fg, insertwidth=3, highlightthickness=0, bd=0)
        self.entry.pack(fill="x", expand=True)
        self.entry.focus_set()

        self.border = tk.Canvas(self, height=2, takefocus=False, bg=fg, borderwidth=0)
        self.border.pack(fill="x", expand=True, side="bottom")

        self.entry.bind("<FocusIn>", self.entry_on_focus)
        self.entry.bind("<FocusOut>", self.entry_on_focus_out)

    @property
    def widget_width(self):
        self.update()
        return self.winfo_width()

    def entry_on_focus(self, _):
        self.border.config(bg=self.fg)

    def entry_on_focus_out(self, _):
        self.border.config(bg=self.bg)
