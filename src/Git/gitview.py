from src.modules import ttk


class GitView(ttk.Frame):
    def __init__(self, master: ttk.Panedwindow, path: str):
        super().__init__(master)
        self.path = path
        master.add(self, text="Git")
