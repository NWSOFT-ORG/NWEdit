from src.constants import APPDIR, logger
from src.modules import json, tk, ttk, ttkthemes, styles, lexers


# Need these because importing settings is a circular import
def get_theme():
    with open(APPDIR + "/Settings/general-settings.json") as f:
        settings = json.load(f)
    return settings["theme"]

def get_font():
    with open(APPDIR + "/Settings/general-settings.json") as f:
        settings = json.load(f)
    return settings["font"]


class YesNoDialog(tk.Toplevel):
    def __init__(self, parent: tk.Misc = None, title: str = "", text: str = None):
        self.text = text
        super().__init__(parent)
        self.title(title)
        label1 = ttk.Label(text=self.text)
        label1.pack(fill="both")

        box = ttk.Frame(self)

        b1 = ttk.Button(box, text="Yes", command=self.apply)
        b1.pack(side="left")
        b2 = ttk.Button(box, text="No", command=self.cancel)
        b2.pack(side="left")

        box.pack(fill="x")
        self.protocol("WM_DELETE_WINDOW", self.cancel)
        self.resizable(0, 0)
        self.wait_window(self)

    def apply(self, _=None):
        self.result = 1
        self.destroy()
        logger.info("apply")

    def cancel(self, _=None):
        """put focus back to the parent window"""
        self.result = 0
        self.destroy()
        logger.info("cancel")


class InputStringDialog(tk.Toplevel):
    def __init__(self, parent='.', title='', text=''):
        super().__init__(parent)
        self.title(title)
        ttk.Label(self, text=text).pack(fill='x')
        self.entry = ttk.Entry(self)
        self.entry.pack(fill="x", expand=1)
        box = ttk.Frame(self)

        b1 = ttk.Button(box, text="Ok", command=self.apply)
        b1.pack(side="left")
        b2 = ttk.Button(box, text="Cancel", command=self.cancel)
        b2.pack(side="left")

        box.pack(fill="x")
        self.protocol("WM_DELETE_WINDOW", self.cancel)
        self.resizable(0, 0)
        self.wait_window(self)

    def apply(self):
        self.result = self.entry.get()
        self.destroy()
        logger.info("apply")
    
    def cancel(self):
        self.result = None
        self.destroy()
        logger.info("cancel")


class ErrorInfoDialog(tk.Toplevel):
    def __init__(self, parent: tk.Misc = None, text: str = None, title: str = "Error"):
        self.text = text
        super().__init__(parent)
        self.title(title)
        label1 = ttk.Label(self, text=self.text)
        label1.pack(side="top", fill="both", expand=1)
        b1 = ttk.Button(self, text="Ok", width=10, command=self.apply)
        b1.pack(side="left")
        self.protocol("WM_DELETE_WINDOW", self.cancel)
        self.resizable(0, 0)
        self.wait_window(self)

    def apply(self, _=None):
        self.destroy()
        logger.info("apply")

    @staticmethod
    def cancel(_=None):
        pass

