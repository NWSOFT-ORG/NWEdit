from src.modules import ttk


class CustomTabs(ttk.Notebook):
    def __init__(self, master, tabpos='sw'):
        self._init_style(tabpos)
        super().__init__(master, style='Panel.TNotebook')

    def _init_style(self, pos):
        self.style = ttk.Style()
        self.style.configure('Panel.TNotebook', tabposition=pos)
        self.style.configure('Panel.TNotebook.Tab', padding=[0, 0, 0, 0])
