from src.constants import OSX
from src.Utils.color_utils import is_dark_color
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
    def __init__(
        self,
        master: [tk.Tk, tk.Toplevel, str],
        title: str,
        disable: bool = True,
        closable: bool = True,
    ):
        super().__init__(master, takefocus=True)
        if OSX:
            self.tk.call(
                "::tk::unsupported::MacWindowStyle", "style", self._w, "simple"
            )
        else:
            self.overrideredirect(True)

        self.title_text = title
        self.title(title)  # Need a decent message to show on the taskbar
        self.master = master
        self.bg = get_bg()
        self.create_titlebar()
        if closable:
            self.close_button()
            self.bind("<Escape>", lambda _: self.destroy())
        self.window_bindings()

        if disable:
            self.wait_visibility(self)
            self.grab_set()  # Linux WMs might fail to grab the window

        self.focus_force()
        self.attributes("-topmost", True)
        self.bind("<Destroy>", self.on_exit)

        size = ttk.Sizegrip(self)
        size.bind("<B1-Motion>", self.resize)
        size.pack(side="bottom", anchor="se")

    def on_exit(self, _):
        # Fix destroy issues, need to relink events.
        self.master.bind("<FocusIn>", lambda _: None)
        self.master.bind("<FocusOut>", lambda _: None)
        self.grab_release()

    def create_titlebar(self):
        self.titleframe = ttk.Frame(self)
        self.titlebar = ttk.Label(self.titleframe, text=self.title_text)
        self.titlebar.pack(side="left", fill="both", expand=1)

        self.titleframe.pack(fill="x", side="top")

    def add_widget(self, child_frame):
        self.child_frame = child_frame
        self.child_frame.pack(fill="both", expand=True)

    def window_bindings(self):
        self.titlebar.bind("<ButtonPress-1>", self.start_move)
        self.titlebar.bind("<ButtonRelease-1>", self.stop_move)
        self.titlebar.bind("<B1-Motion>", self.do_move)
        self.master.bind("<FocusIn>", lambda _: self.focus_force())

    def start_move(self, event):
        self.x = event.x
        self.y = event.y

    def stop_move(self, _):
        self.x = None
        self.y = None

    def do_move(self, event):
        x = event.x - self.x + self.winfo_x()
        y = event.y - self.y + self.winfo_y()
        self.geometry(f"+{x}+{y}")

    def resize(self, event: tk.Event):
        cursor_x = event.x_root
        cursor_y = event.y_root
        window_x = self.winfo_rootx()
        window_y = self.winfo_rooty()
        self.geometry(f"{cursor_x - window_x}x{cursor_y - window_y}")
        return

    def close_button(self):
        if is_dark_color(self.bg):
            close_icon = tk.PhotoImage(file="Images/close.gif")
        else:
            close_icon = tk.PhotoImage(file="Images/close-dark.gif")

        close_button = ttk.Label(self.titleframe)
        close_button.image = close_icon
        close_button.config(image=close_icon)
        close_button.pack(side="left")

        close_button.bind("<ButtonRelease>", lambda _: self.destroy())
