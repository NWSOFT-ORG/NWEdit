from src.dialogs import get_theme
from src.functions import darken_color
from src.modules import tk, ttk, ttkthemes


class Navigate:
    def __init__(self, tabwidget: ttk.Notebook, tablist: dict):
        self.text: tk.Text = tablist[tabwidget.nametowidget(tabwidget.select())].textbox
        if self.text.navigate or self.text.searchable:
            return
        self.text.navigate = True
        self.goto_frame = ttk.Frame(self.text.frame)
        self._style = ttkthemes.ThemedStyle()
        self._style.set_theme(get_theme())
        bg = self._style.lookup("TLabel", "background")
        fg = self._style.lookup("TLabel", "foreground")
        self.goto_frame.pack(anchor="nw")
        ttk.Label(self.goto_frame, text="Go to place: [Ln].[Col] ").pack(side="left")
        self.place = tk.Entry(
            self.goto_frame,
            background=darken_color(bg, 30, 30, 30),
            foreground=fg,
            insertbackground=fg,
            highlightthickness=0,
        )
        self.place.focus_set()
        self.place.pack(side="left", anchor="nw")
        ttk.Button(self.goto_frame, command=self._goto, text=">> Go to").pack(
            side="left", anchor="nw"
        )
        ttk.Button(self.goto_frame, text="x", command=self._exit, width=1).pack(
            side="left", anchor="nw"
        )
        self.statuslabel = ttk.Label(self.goto_frame, foreground="red")
        self.statuslabel.pack(side="left", anchor="nw")

    def check(self) -> bool:
        index = self.place.get().split(".")
        lines = int(float(self.text.index("end")))
        if (not len(index) == 2) or index[0] > lines:
            self.statuslabel.config(text=f'Error: invalid index: {".".join(index)}')
            return False
        return True

    def _goto(self):
        try:
            if self.check():
                currtext = self.text
                currtext.mark_set("insert", self.place.get())
                currtext.see("insert")
                self._exit()
                return
        except tk.TclError:
            self.check()

    def _exit(self):
        self.goto_frame.pack_forget()
        self.text.focus_set()
        self.text.navigate = False
