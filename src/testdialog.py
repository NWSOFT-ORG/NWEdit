from src.modules import tk, ttk
from src.tktext import EnhancedTextFrame
from src.dialogs import InputStringDialog


class TestDialog(tk.Toplevel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title("Unit Tests")
        self.resizable(0, 0)
        self.tests_listbox = ttk.Treeview(self)
        self.tests_listbox.pack(fill="both")
        self.button_frame = ttk.Frame(self)
        ttk.Button(self.button_frame, text="New").pack()
        ttk.Button(self.button_frame, text="Delete").pack()
        ttk.Button(self.button_frame, text="Edit").pack()
        self.button_frame.pack(side="bottom")
        self.mainloop()

    def new(self):
        dialog = InputStringDialog(self.master, 'New', 'Name')
        name = dialog.result
        print(name)

    def delete(self):
        pass

    def edit(self):
        pass
