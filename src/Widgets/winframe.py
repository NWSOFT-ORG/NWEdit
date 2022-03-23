from src.functions import is_dark_color
from src.modules import ttk, tk, ttkthemes, json


# Need these because importing settings is a circular import
def get_theme():
    with open("Config/general-settings.json") as f:
        settings = json.load(f)
    return settings["theme"]


def get_bg():
    style = ttkthemes.ThemedStyle()
    style.set_theme(get_theme())
    return style.lookup("TLabel", "background")


class WinFrame(tk.Toplevel):
    def __init__(self, master, title, disable=True):
        super().__init__(master)
        self.overrideredirect(False)
        self.overrideredirect(True)
        self.title = title
        self.master = master
        self.bg = get_bg()

        if disable:
            self.grab_set()

        self.create_titlebar()
        self.close_button()
        self.window_bindings()
        self.focus_set()
        self.tkraise()

    def create_titlebar(self):
        self.titleframe = ttk.Frame(self)
        self.titlebar = ttk.Label(self.titleframe, text=self.title)
        self.titlebar.pack(side='left', fill='both', expand=1)

        self.titleframe.pack(fill='x', side='top')

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

    def stop_move(self, _):
        self.x = None
        self.y = None

    def do_move(self, event):
        x = (event.x - self.x + self.winfo_x())
        y = event.y - self.y + self.winfo_y()
        self.geometry(f"+{x}+{y}")

    def close_button(self):
        if is_dark_color(self.bg):
            close_icon = tk.PhotoImage(file='Images/close.gif')
        else:
            close_icon = tk.PhotoImage(file='Images/close-dark.gif')

        close_button = ttk.Label(self.titleframe)
        close_button.image = close_icon
        close_button.config(image=close_icon)
        close_button.pack(side='left')

        close_button.bind('<ButtonRelease>', lambda _: self.destroy())
