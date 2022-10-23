from tkinter import ttk


def bind_events(label):
    label.bind("<Leave>", lambda _=None: label.state(("!active",)))
    label.bind("<Enter>", lambda _=None: activate(label))


def activate(label):
    if label["text"]:
        label.state(("active",))


class Statusbar(ttk.Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        style = ttk.Style(self)
        style.configure("TLabel", padding=[3, 1, 1, 3])
        ttk.Label(self, text="NWEdit").pack(side="left")
        ttk.Sizegrip(self).pack(side="right")

        self.label3 = ttk.Label(self)
        self.label3.pack(side="right")
        bind_events(self.label3)

        self.pack(side="bottom", anchor="nw", fill="x")
