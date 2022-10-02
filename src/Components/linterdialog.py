from tkinter import ttk


class LinterDialog(ttk.Frame):
    def __init__(self, bottom_frame: ttk.Notebook):
        super().__init__()
        bottom_frame.add(self, text="Linter")
