from modules import *


class Statusbar:
    def __init__(self):
        self.statusbar = ttk.Frame()
        self.statusbar.pack(side='bottom', fill='x', anchor='nw')
        self.label1 = ttk.Label(self.statusbar, text='PyPlus |')
        self.label1.pack(side='left')
        self.label2 = ttk.Label(self.statusbar)
        self.label2.pack(side='left')
        self.label3 = ttk.Label(self.statusbar)
        self.label3.pack(side='left')
        self.statusbar.pack(side='left', anchor='nw')
