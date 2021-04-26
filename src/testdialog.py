from src.modules import tk, ttk, os
from src.tktext import EnhancedTextFrame
from src.dialogs import InputStringDialog


class TestDialog(tk.Toplevel):
    def __init__(self, parent, path):
        if parent:
            super().__init__(parent)
            self.transient(parent)
        if not os.path.exists(os.path.join(path, 'test.py')):
            with open(os.path.join(path, 'test.py'), 'w') as f:
                f.write('')
        self.title("Unit Tests")
        self.resizable(0, 0)
        self.tests_listbox = ttk.Treeview(self, show="tree")
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
        codewin.geometry('500x300')
        codewin.resizable(0, 0)
        codewin.transient(self)
        textframe = EnhancedTextFrame(codewin)
        textframe.pack(fill="both")
        button_frame = ttk.Frame(codewin)
        okbtn = ttk.Button(button_frame, text='OK')
        okbtn.pack()
        cancelbtn = ttk.Button(button_frame, text='Cancel')
        cancelbtn.pack()
        button_frame.pack()
        codewin.mainloop()

    def delete(self):
        pass

    def edit(self):
        pass
