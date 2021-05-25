from src.constants import APPDIR
from src.modules import lexers, os, subprocess, tk, ttk
from src.tktext import EnhancedTextFrame
from src.highlighter import create_tags, recolorize


class CommitView(ttk.Frame):
    def __init__(self, parent, path):
        super().__init__(parent)
        parent.forget(parent.panes()[0])
        self.pack(fill='both', expand=1)
        parent.insert('0', self)

        self.dir = path
        self.master = parent
        difftext.config(state="disabled", wrap="none")
        textframe.pack(fill="both")
        diffwindow.mainloop()
