from src.constants import APPDIR, logger
from src.modules import json, tk, ttk, ttkthemes, styles, lexers
import ast
import traceback


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
        super().__init__(parent, title)
        label1 = ttk.Label(text=self.text)
        label1.pack(fill="both")

        box = ttk.Frame(self)

        b1 = ttk.Button(box, text="Yes", width=10, command=self.apply)
        b1.pack(side="left", padx=5, pady=5)
        b2 = ttk.Button(box, text="No", width=10, command=self.cancel)
        b2.pack(side="left", padx=5, pady=5)

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
    def __init__(self, parent, title, text):
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
        super().__init__(parent, title)
        label1 = ttk.Label(master, text=self.text)
        label1.pack(side="top", fill="both", expand=1)
        b1 = ttk.Button(self, text="Ok", width=10, command=self.apply)
        b1.pack(side="left", padx=5, pady=5)
        self.protocol("WM_DELETE_WINDOW", self.cancel)
        self.resizable(0, 0)
        self.wait_window(self)

    def apply(self, _=None):
        self.destroy()
        logger.info("apply")

    @staticmethod
    def cancel(_=None):
        pass


class CodeListDialog(ttk.Frame):
    def __init__(self, parent=None, text=None, file=None):
        super().__init__(parent)
        self.file = file
        self.text = text

        self.state_label = ttk.Label(self, text='')
        self.state_label.pack(anchor='nw', fill='x')
        self.tree = ttk.Treeview(self, show='tree')
        self.tree.bind('<Double-1>', self.double_click)
        self.tree.pack(fill='both', expand=1)

        self.show_items()
        self.pack(fill='both', expand=1)
        parent.forget(parent.panes()[0])
        parent.insert('0', self)
    
    def show_items(self):
        filename = self.file
        with open(filename) as f:
            try:
                node = ast.parse(f.read())
            except Exception:
                self.state_label.configure(text=f'Error: Cannot parse docoment.\n {traceback.format_exc()}',
                                           foreground='red')
                return

        functions = [_obj for _obj in node.body if isinstance(_obj, ast.FunctionDef)]
        classes = [_obj for _obj in node.body if isinstance(_obj, ast.ClassDef)]
        defined_vars = [_obj for _obj in node.body if isinstance(_obj, ast.Assign)]


        for function in functions:
            self.show_info("", function, 'func')

        for class_ in classes:
            parent = self.show_info("", class_, 'class')
            methods = [_obj for _obj in class_.body if isinstance(_obj, ast.FunctionDef)]
            defined_vars = [_obj.targets for _obj in class_.body if isinstance(_obj, ast.Assign)]
            for method in methods:
                self.show_info(parent, method, 'func')
            
            for var in defined_vars:
                self.show_var(parent, var)
        
        for var in defined_vars:
            self.show_var("", var)
    
    def show_info(self, parent, _obj, _type=''):
        return self.tree.insert(parent,
                                "end", text=f"{_obj.name} [{_obj.lineno}:{_obj.col_offset}]",
                                tags=[_type])
    
    def show_var(self, parent,  _obj):
        for item in _obj.targets:
            self.tree.insert(parent, 'end',
                             text=f'{item.id} [{item.lineno}:{item.col_offset}]')
    
    def double_click(self, _=None):
        try:
            item = self.tree.focus()
            text = self.tree.item(item, 'text')
            index = text.split(' ')[-1][1:-1]
            line = index.split(':')[0]
            col = index.split(':')[1]
            self.text.mark_set('insert', f"{line}.{col}")
            self.text.see('insert')
            self.text.focus_set()

        except IndexError:  # Click on empty places
            pass
