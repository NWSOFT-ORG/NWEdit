from src.modules import ttk, ttkthemes
from src.settings import Settings


class CustomMenubar(ttk.Frame):
    def __init__(self, *args, **kwargs):
        ttk.Frame.__init__(self, *args, **kwargs)
        self._opened_menu = None
        self._opened_menu = None
        settings = Settings()
        theme = settings.get_settings("theme")
        self._style = ttkthemes.ThemedStyle()
        self._style.set_theme(theme)

    def add_cascade(self, label, menu):
        label_widget = ttk.Label(
            self,
            text=label,
            padding=[6, 1, 1, 1],
            font="Arial 10",
        )
        bg = self._style.lookup("TLabel", "background")
        fg = self._style.lookup("TLabel", "foreground")

        menu.config(
            cursor="left_ptr",
            activebackground=fg,
            activeforeground=bg,
            bg=bg,
            fg=fg,
            relief="ridge",
        )

        label_widget.pack(side="left")

        def enter(event):
            label_widget.state(("active",))
            if self._opened_menu is not None:
                self._opened_menu.unpost()
                click(event)

        def leave(_):
            label_widget.state(("!active",))

        def click(_):
            try:
                self._opened_menu = menu
                menu.tk_popup(
                    label_widget.winfo_rootx(),
                    label_widget.winfo_rooty() + label_widget.winfo_height(),
                )
            finally:
                self._opened_menu = None

        label_widget.bind("<Enter>", enter, True)
        label_widget.bind("<Leave>", leave, True)
        label_widget.bind("<1>", click, True)
