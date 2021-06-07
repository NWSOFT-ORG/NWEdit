from src.constants import APPDIR, logger
from src.modules import json, tk, ttk, styles

from src.tktext import EnhancedTextFrame

# Need these to prevent circular imports
def get_pygments():
    with open(APPDIR + "/Settings/general-settings.json") as f:
        settings = json.load(f)
    return settings["pygments"]

def get_font():
    with open(APPDIR + "/Settings/general-settings.json") as f:
        settings = json.load(f)
    return settings["font"]


class ReadonlyText(EnhancedTextFrame):
    def __init__(self, master):
        super().__init__(master)
        style = styles.get_style_by_name(get_pygments())
        bgcolor = style.background_color
        fgcolor = style.highlight_color
        self.text.configure(state='disabled',
                       fg=fgcolor, bg=bgcolor,
                       font=get_font())

    def insert(self, pos, text):
        self.text.configure(state='normal')
        self.text.insert(pos, text)
        self.text.configure(state='disabled')
    
    def delete(self, pos1, pos2):
        self.text.configure(state='normal')
        self.text.delete(pos1, pos2)
        self.text.configure(state='disabled')


class ErrorReportDialog(tk.Toplevel):
    def __init__(self, error_name, error_message):
        super().__init__()
        self.title(error_name)
        self.master.withdraw()
        ttk.Label(self, text='Please consider reporting a bug on github.').pack(anchor='nw', fill='x')
        text = ReadonlyText(self)
        text.insert('end', error_message)
        text.pack(fill='both')
        self.mainloop()


class LogViewDialog(tk.Toplevel):
    def __init__(self):
        super().__init__()
        self.title('Log view')
        frame = ttk.Frame(self)
        frame.pack(anchor='nw', fill='x')
        ttk.Label(frame, text='Debug log').pack(anchor='nw', side='left')
        ttk.Button(frame, text='Copy', command=self.copy_log).pack(side='right')
        self.log_text = ReadonlyText(self)
        self.log_text.pack(fill='both', expand=1)
        self.log_text.after(10, self.update_log)
        self.mainloop()
    
    def update_log(self):
        with open('pyplus.log') as f:
            log = f.read()
        self.log_text.delete('1.0', 'end')
        self.log_text.insert('end', log)
        self.log_text.text.see('end')
        self.log_text.after(10, self.update_log)
    
    def copy_log(self):
        self.log_text.clipboard_clear()
        self.log_text.clipboard_append(
            self.log_text.get('1.0', 'end')
        )