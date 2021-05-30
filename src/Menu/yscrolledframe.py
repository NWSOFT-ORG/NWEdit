from src.modules import tk, ttk


class ScrollableFrame(ttk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.canvas = tk.Canvas(self)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.frame = ttk.Frame(self.canvas)

        self.canvas.create_window(0, 0, window=self.frame, anchor="nw")

        self.frame.bind("<Configure>", self.config_canvas)

        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
    
    def config_canvas(self, _=None):
        self.canvas.configure(
            scrollregion=self.canvas.bbox("all"),
            width=self.frame.winfo_width())
        if self.frame.winfo_height() < self.canvas.winfo_height():
            self.canvas.configure(
                height=self.frame.winfo_height()
            )
            self.scrollbar.pack_forget()
        else:
            self.scrollbar.pack(side="right", fill="y")
