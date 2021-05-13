from src.modules import ttk


class Statusbar(ttk.Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label1 = ttk.Label(self, text="PyPlus")
        self.label1.pack(side="left")
        ttk.Separator(self, orient='vertical').pack(side='left', fill='y')
        self.label2 = ttk.Label(self)
        self.label2.pack(side="left")
        ttk.Separator(self, orient='vertical').pack(side='left', fill='y')
        ttk.Sizegrip(self).pack(side="right")
        self.label3 = ttk.Label(self)
        self.label3.pack(side="right")
        ttk.Separator(self, orient='vertical').pack(side="right", fill='y')
        self.pack(side="bottom", anchor="nw", fill="x")
