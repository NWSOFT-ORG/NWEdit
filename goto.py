from modules import (tk, ttk)


class Navigate:
    def __init__(self, tabwidget: ttk.Notebook, tablist: dict):
        self.text: tk.Text = tablist[tabwidget.nametowidget(
            tabwidget.select())].textbox
        self.goto_frame = ttk.Frame(self.text.frame)
        self.goto_frame.pack(anchor="nw")
        ttk.Label(self.goto_frame, text="Go to place: [Ln].[Col] ").pack(
            side="left")
        self.place = tk.Entry(
            self.goto_frame,
            background="black",
            foreground="white",
            insertbackground="white",
            highlightthickness=0,
        )
        self.place.focus_set()
        self.place.pack(side="left", anchor='nw')
        self.place.bind("<Key>", self.check)
        ttk.Button(self.goto_frame, command=self._goto, text=">> Go to").pack(side='left', anchor='nw')
        ttk.Button(self.goto_frame, text="x", command=self._exit, width=1).pack(
            side="left", anchor='nw'
        )
        self.statuslabel = ttk.Label(self.goto_frame, foreground='red')
        self.statuslabel.pack(side='left', anchor='nw')

    def check(self) -> bool:
        index = self.place.get().split('.')
        if not len(index) == 2:
            self.statuslabel.config(
                text=f'Error: invalid index: {".".join(index)}')
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
