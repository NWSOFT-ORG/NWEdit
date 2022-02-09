from src.modules import ttk


class WinFrame(ttk.Frame):
    def __init__(self, master, title):
        super().__init__(master)
        self.title = title
        self.master = master

        self.titlebar()
        self.window_bindings()
        self.place(relx=.5, rely=.5, anchor="center")

    def titlebar(self):
        self.titlebar = ttk.Label(self, text=self.title)
        self.titlebar.pack(fill='x', side='top')

    def add_widget(self, child_frame):
        self.child_frame = child_frame
        self.configure(borderwidth=1, relief='ridge')
        self.child_frame.pack(fill='both')

    def window_bindings(self):
        self.titlebar.bind("<ButtonPress-1>", self.start_move)
        self.titlebar.bind("<ButtonRelease-1>", self.stop_move)
        self.titlebar.bind("<B1-Motion>", self.do_move)

    def start_move(self, event):
        self.x = event.x
        self.y = event.y

    def stop_move(self, event):
        self.x = None
        self.y = None

    def do_move(self, event):
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.winfo_x() + deltax
        y = self.winfo_y() + deltay
        self.place_configure(y=y, x=x)
