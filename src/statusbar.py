from src.modules import ttk


    
def bind_events(label):
    label.bind('<Leave>', lambda _=None: label.state(('!active',)))
    label.bind('<Enter>', lambda _=None: label.state(('active',)))


class Statusbar(ttk.Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        style = ttk.Style(self)
        style.configure('TLabel', padding=[3, 1, 1, 3])

        self.label1 = ttk.Label(self, text="PyPlus")
        self.label1.pack(side="left")
        bind_events(self.label1)

        self.label2 = ttk.Label(self)
        self.label2.pack(side="left")
        bind_events(self.label2)

        ttk.Sizegrip(self).pack(side="right")

        self.label3 = ttk.Label(self)
        self.label3.pack(side="right")
        bind_events(self.label3)

        self.pack(side="bottom", anchor="nw", fill="x")
