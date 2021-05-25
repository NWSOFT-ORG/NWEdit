from src.constants import APPDIR, logger
from src.modules import json, tk, ttk, ttkthemes, styles, lexers
import ast


# Need these because importing settings is a circular import
def get_theme():
    with open(APPDIR + "/Settings/general-settings.json") as f:
        settings = json.load(f)
    return settings["theme"]

def get_font():
    with open(APPDIR + "/Settings/general-settings.json") as f:
        settings = json.load(f)
    return settings["font"]


class Dialog(tk.Toplevel):
    def __init__(self, parent: tk.Misc = None, title: str = None):
        if parent:
            super().__init__(parent)
            self.transient(parent)
        else:
            super().__init__()
            self.transient(".")

        if title:
            self.title(title)

        self.result = None
        self._style = ttkthemes.ThemedStyle()
        self._style.set_theme(get_theme())
        bg = self._style.lookup("TLabel", "background")

        self.config(background=bg)

        body = ttk.Frame(self)
        self.initial_focus = self.body(body)
        body.pack(fill="x", padx=5, pady=5)

        self.buttonbox()

        if not self.initial_focus:
            self.initial_focus = self

        self.protocol("WM_DELETE_WINDOW", self.cancel)

        self.initial_focus.focus_set()
        self.resizable(0, 0)
        self.wait_window(self)

    def body(self, master: tk.Misc):
        """create dialog body.  return widget that should have
        initial focus.  this method should be overridden
        """

        return master

    def buttonbox(self):
        """add standard button box. override if you don't want the
        standard buttons
        """

        box = ttk.Frame(self)

        w = ttk.Button(box, text="OK", width=10, command=self.ok)
        w.pack(side="left", padx=5, pady=5)
        w = ttk.Button(box, text="Cancel", width=10, command=self.cancel)
        w.pack(side="left", padx=5, pady=5)

        box.pack(fill="x")

    def ok(self, _=None):
        if not self.validate():
            self.initial_focus.focus_set()  # put focus back
            return

        self.withdraw()
        self.update_idletasks()

        self.apply()

        self.cancel()

    def cancel(self, _=None):
        self.destroy()

    @staticmethod
    def validate(_=None):
        return 1  # override

    @staticmethod
    def apply(_=None):
        pass  # override


class YesNoDialog(Dialog):
    def __init__(self, parent: tk.Misc = None, title: str = "", text: str = None):
        self.text = text
        super().__init__(parent, title)

    def body(self, master):
        label1 = ttk.Label(master, text=self.text)
        label1.pack(fill="both")

        return label1

    def buttonbox(self):
        box = ttk.Frame(self)

        b1 = ttk.Button(box, text="Yes", width=10, command=self.apply)
        b1.pack(side="left", padx=5, pady=5)
        b2 = ttk.Button(box, text="No", width=10, command=self.cancel)
        b2.pack(side="left", padx=5, pady=5)

        box.pack(fill="x")
        return box

    def apply(self, _=None):
        self.result = 1
        self.destroy()
        logger.info("apply")

    def cancel(self, _=None):
        """put focus back to the parent window"""
        self.result = 0
        self.destroy()
        logger.info("cancel")


class InputStringDialog(Dialog):
    def __init__(self, parent=None, title="InputString", text=""):
        self.text = text
        super().__init__(parent, title)

    def body(self, master: tk.Misc):
        label1 = ttk.Label(master, text=self.text)
        label1.pack(side="top", fill="both", expand=1)

        return label1

    def buttonbox(self):
        self.entry = ttk.Entry(self)
        self.entry.pack(fill="x", expand=1)
        box = ttk.Frame(self)

        b1 = ttk.Button(box, text="Ok", width=10, command=self.apply)
        b1.pack(side="left", padx=5, pady=5)
        b2 = ttk.Button(box, text="Cancel", width=10, command=self.cancel)
        b2.pack(side="left", padx=5, pady=5)

        box.pack(fill="x")
        return box

    def apply(self, _=None):
        self.result = self.entry.get()
        self.destroy()
        logger.info("apply")

    def cancel(self, _=None):
        """put focus back to the parent window"""
        self.result = 0
        self.destroy()
        logger.info("cancel")


class ErrorInfoDialog(Dialog):
    def __init__(self, parent: tk.Misc = None, text: str = None, title: str = "Error"):
        self.text = text
        super().__init__(parent, title)

    def body(self, master):
        label1 = ttk.Label(master, text=self.text)
        label1.pack(side="top", fill="both", expand=1)

        return label1

    def buttonbox(self):
        b1 = ttk.Button(self, text="Ok", width=10, command=self.apply)
        b1.pack(side="left", padx=5, pady=5)

    def apply(self, _=None):
        self.destroy()
        logger.info("apply")

    @staticmethod
    def cancel(_=None):
        pass


class ViewDialog(ttk.Frame):
    def __init__(self, parent=None, text=None, file=None):
        super().__init__(parent)
        self.file = file
        self.text = text
        self.tree = ttk.Treeview(self)
        self.tree.bind('<Double-1>', self.double_click)
        self.tree.pack(fill='both', expand=1)
        ttk.Button(self, text="Ok", command=self.destroy).pack(side="left")
        self.show_items()
        self.pack(fill='both', expand=1)
        parent.forget(parent.panes()[0])
        parent.insert('0', self)
    
    def show_items(self):
        filename = self.file
        with open(filename) as f:
            node = ast.parse(f.read())

        functions = [_obj for _obj in node.body if isinstance(_obj, ast.FunctionDef)]
        classes = [_obj for _obj in node.body if isinstance(_obj, ast.ClassDef)]

        for function in functions:
            self.show_info("", function)

        for class_ in classes:
            parent = self.show_info("", class_)
            methods = [n for n in class_.body if isinstance(n, ast.FunctionDef)]
            for method in methods:
                self.show_info(parent, method)
    
    def show_info(self, parent, _obj):
        return self.tree.insert(parent, "end", text=f"{_obj.name} [{_obj.lineno}:{_obj.col_offset}]")
    
    def double_click(self, _=None):
        item = self.tree.focus()
        text = self.tree.item(item, 'text')
        index = text.split(' ')[-1][1:-1]
        line = index.split(':')[0]
        col = index.split(':')[1]
        self.text.mark_set('insert', f"{line}.{col}")
        self.text.see('insert')
        self.text.focus_set()
        self.destroy()
