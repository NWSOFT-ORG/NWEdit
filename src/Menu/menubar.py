from src.Dialog.commondialog import get_theme
from src.Widgets.statusbar import bind_events
from src.modules import font, tk, ttk, ttkthemes


def get_font_height(text: str) -> int:
    """Dynamically adjust label height to font height"""
    style = ttkthemes.ThemedStyle()
    style.set_theme(get_theme())
    font_name = style.lookup('TLabel', 'font')

    render_font = font.Font(font=font_name)
    return render_font.measure(text)



class MenuBar(ttk.Frame):
    def __init__(self, parent: [tk.Tk, tk.Toplevel]) -> None:
        super().__init__(parent)
        self.master = parent
        self.pack(fill='x', side='top')

    def add_cascade(self, label: str, menu) -> None:
        menu_label = ttk.Label(self, text=label)
        menu_label.bind("<Button>", lambda _: self.show(menu_label, menu))

        bind_events(menu_label)

        height = get_font_height(label)
        self.configure(height=height)
        menu_label.pack(side='left')

    @staticmethod
    def show(menu_label: ttk.Label, menu: tk.Menu) -> None:
        x_pos = menu_label.winfo_rootx()
        y_pos = menu_label.winfo_rooty() + menu_label.winfo_height()
        menu.tk_popup(x_pos, y_pos)
