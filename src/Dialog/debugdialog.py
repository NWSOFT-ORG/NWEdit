from src.constants import APPDIR
from src.modules import json, tk, ttk, styles

from src.Widgets.tktext import EnhancedTextFrame


# Need these to prevent circular imports
def get_pygments() -> str:
    with open(APPDIR + "/Config/general-settings.json") as f:
        settings = json.load(f)
    return settings["pygments"]


def get_font() -> str:
    with open(APPDIR + "/Config/general-settings.json") as f:
        settings = json.load(f)
    return settings["font"]


class ReadonlyText(EnhancedTextFrame):
    def __init__(self, master: tk.Misc) -> None:
        super().__init__(master)
        style = styles.get_style_by_name(get_pygments())
        bgcolor = style.background_color
        fgcolor = "#f00"
        self.text.configure(state='disabled',
                            fg=fgcolor, bg=bgcolor,
                            font=get_font())

    def insert(self, pos: [int, str], text: str) -> None:
        # Free the text first
        self.text.configure(state='normal')
        self.text.insert(pos, text)
        self.text.configure(state='disabled')

    def delete(self, pos1: [int, str], pos2: [int, str]) -> None:
        # Free the text first
        self.text.configure(state='normal')
        self.text.delete(pos1, pos2)
        self.text.configure(state='disabled')


class ErrorReportDialog(tk.Toplevel):
    def __init__(self, error_name: str, error_message: str) -> None:
        super().__init__()
        self.title(error_name)
        # noinspection PyUnresolvedReferences
        self.master.withdraw()
        ttk.Label(self, text='Please consider reporting a bug on github.').pack(anchor='nw', fill='x')
        text = ReadonlyText(self)
        text.insert('end', error_message)
        text.pack(fill='both')

        self.protocol('WM_DELETE_WINDOW', self.exit)
        self.mainloop()

    def exit(self) -> None:
        self.master.destroy()
        exit(1)


class LogViewDialog(tk.Toplevel):
    def __init__(self) -> None:
        super().__init__()
        self.title('Log view')
        frame = ttk.Frame(self)
        frame.pack(anchor='nw', fill='x')
        ttk.Label(frame, text='Debug log').pack(anchor='nw', side='left')
        ttk.Button(frame, text='Copy', command=self.copy_log).pack(side='right')
        self.log_text = ReadonlyText(self)
        self.log_text.pack(fill='both', expand=True)
        self.log_text.after(10, self.update_log)
        self.mainloop()

    def update_log(self) -> None:
        with open('pyplus.log') as f:
            log = f.read()
        self.log_text.delete('1.0', 'end')
        self.log_text.insert('end', log)
        self.log_text.text.see('end')
        self.log_text.after(10, self.update_log)

    def copy_log(self) -> None:
        self.log_text.clipboard_clear()
        self.log_text.clipboard_append(
            self.log_text.get('1.0', 'end')
        )
