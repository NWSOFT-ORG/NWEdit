from modules import *


class Statusbar(ttk.Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label1 = ttk.Label(self, text='PyPlus |')
        self.label1.pack(side='left')
        self.label2 = ttk.Label(self)
        self.label2.pack(side='left')
        self.label3 = ttk.Label(self)
        self.label3.pack(side='left')
        self.pack(side='left', anchor='nw')
