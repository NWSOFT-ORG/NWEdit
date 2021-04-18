from modules import tk, ttk
from tktext import EnhancedTextFrame


class TestDialog(tk.Toplevel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title("Unit Tests")
        self.resizable(0, 0)
        self.tests_listbox = tk.Listbox(self)
        self.tests_listbox.pack(fill="both")
        self.button_frame = ttk.Frame(self)
        ttk.Button(self.button_frame, text="New").pack()
        ttk.Button(self.button_frame, text="Delete").pack()
        ttk.Button(self.button_frame, text="Edit").pack()
        self.button_frame.pack(side="bottom")

    def new(self):
        pass

    def delete(self):
        pass

    def edit(self):
        pass
