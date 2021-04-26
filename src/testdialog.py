from src.modules import tk, ttk
from src.tktext import EnhancedTextFrame
from src.dialogs import InputStringDialog


class TestDialog(tk.Toplevel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if args:
            self.transient(args[0])
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
        codewin.resizable(0, 0)
        codewin.transient(self)
        textframe = EnhancedTextFrame(codewin)
        textframe.pack(fill="both")
        codewin.mainloop()

    def delete(self):
        pass

    def edit(self):
        pass
