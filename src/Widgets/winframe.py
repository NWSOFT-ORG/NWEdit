from src.modules import ttk, tk
from src.functions import is_dark_color


class WinFrame(tk.Toplevel):
    def __init__(self, master: tk.Tk, title: str = "Title", bg: str = "#000000", disable: bool = True) -> None:
        super().__init__(master)
        self.transient(master)
        self.overrideredirect(True)

        self.title = title
        self.master = master
        self.bg = bg

        if disable:
            master.wait_visibility(self)
            self.grab_set()

        self.create_title()
        self.close_button()
        self.window_bindings()

    def create_title(self) -> None:
        self.titleframe = ttk.Frame(self)
        self.titlebar = ttk.Label(self.titleframe, text=self.title)
        self.titlebar.pack(side='left', fill='both', expand=True)

        self.titleframe.pack(fill='x', side='top')

    def add_widget(self, child_frame: [tk.Widget, object, tk.Misc]) -> None:
        self.child_frame = child_frame
        self.configure(borderwidth=1)
        self.child_frame.pack(fill='both')

    def window_bindings(self) -> None:
        self.titlebar.bind("<ButtonPress-1>", self.start_move)
        self.titlebar.bind("<ButtonRelease-1>", self.stop_move)
        self.titlebar.bind("<B1-Motion>", self.do_move)

    def start_move(self, event: tk.Event) -> None:
        self.x = event.x
        self.y = event.y

    def stop_move(self, _: tk.Event) -> None:
        self.x = None
        self.y = None

    def do_move(self, event: tk.Event) -> None:
        x = (event.x - self.x + self.winfo_x())
        y = (event.y - self.y + self.winfo_y())
        self.geometry(f"+{x}+{y}")

    def close_button(self) -> None:
        if is_dark_color(self.bg):
            close_icon = tk.PhotoImage(file='Images/close.gif')
        else:
            close_icon = tk.PhotoImage(file='Images/close-dark.gif')

        close_button = ttk.Label(self.titleframe)
        close_button.image = close_icon
        close_button.config(image=close_icon)
        close_button.pack(side='left')

        close_button.bind('<ButtonRelease>', lambda _: self.destroy())
