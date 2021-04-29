from src.dialogs import InputStringDialog
from src.modules import os, tk, ttk, inspect, imp
from src.tktext import EnhancedTextFrame


class TestDialog(tk.Toplevel):
    def __init__(self, parent, path):
        if parent:
            super().__init__(parent)
            self.transient(parent)
        if not os.path.exists(os.path.join(path, "test.py")):
            with open(os.path.join(path, "test.py"), "w") as f:
                f.write("")
            self.transient(parent)
        if not os.path.exists(os.path.join(path, "__init__.py")):
            with open(os.path.join(path, "__init__.py"), "w") as f:
                f.write("")

        test_module = imp.load_source('__main__', os.path.join(path, "test.py"))

        test_class = [x[1] for x in inspect.getmembers(
            test_module, inspect.isclass)][0]
        method_list = [x[0] for x in inspect.getmembers(
            test_class, predicate=inspect.isfunction)]
        self.title("Unit Tests")
        self.resizable(0, 0)
        self.tests_listbox = ttk.Treeview(self, show="tree")
        for test in method_list:
            self.tests_listbox.insert('', 'end', text=test)
        self.tests_listbox.pack(fill="both")
        self.button_frame = ttk.Frame(self)
        ttk.Button(self.button_frame, text="New", command=self.new).pack(side="left")
        ttk.Button(self.button_frame, text="Delete").pack(side="left")
        ttk.Button(self.button_frame, text="Edit").pack(side="left")
        self.button_frame.pack(side="bottom")
        self.mainloop()

    def new(self):
        dialog = InputStringDialog(self.master, "New", "Name")
        name = dialog.result
        if not name:
            return
        name = "test_" + name
        codewin = tk.Toplevel(self)
        codewin.resizable(0, 0)
        codewin.transient(self)
        textframe = EnhancedTextFrame(codewin)
        textframe.pack(fill="both")
        button_frame = ttk.Frame(codewin)
        okbtn = ttk.Button(button_frame, text="OK")
        okbtn.pack(side='left')
        cancelbtn = ttk.Button(button_frame, text="Cancel")
        cancelbtn.pack(side='left')
        button_frame.pack(fill='x')
        codewin.mainloop()

    def delete(self):
        pass

    def edit(self):
        pass
