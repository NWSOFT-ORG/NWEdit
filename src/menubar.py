from modules import tk, ttk, ttkthemes
from settings import Settings


class CustomMenubar(ttk.Frame):
    def __init__(self, master):
        ttk.Frame.__init__(self, master)
        self._menus = []
        self._opened_menu = None
        settings = Settings()
        theme = settings.get_settings('theme')
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

        menu.config(cursor='left_ptr', activebackground=fg, activeforeground=bg, bg=bg, fg=fg, relief='ridge')
        if len(self._menus) == 0:
            padx = (6, 0)
        else:
            padx = 0

        label_widget.grid(row=0, column=len(self._menus), padx=padx)

        def enter(_):
            label_widget.state(("active",))

            # Don't know how to open this menu when another menu is open
            # another tk_popup just doesn't work unless old menu is closed by click or Esc
            # https://stackoverflow.com/questions/38081470/is-there-a-way-to-know-if-tkinter-optionmenu-dropdown-is-active
            # unpost doesn't work in Win and Mac: https://www.tcl.tk/man/tcl8.5/TkCmd/menu.htm#M62
            # print("ENTER", menu, self._opened_menu)
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
        self._menus.append(menu)