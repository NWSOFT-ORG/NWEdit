from src.modules import ttk


class GitView(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        master.add(self, text="Git")
