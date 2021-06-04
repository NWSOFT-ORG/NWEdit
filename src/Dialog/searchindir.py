from src.Dialog.commondialog import get_theme
from src.functions import darken_color
from src.modules import tk, ttk, ttkthemes, os
from src.Dialog.search import finditer_withlineno, find_all
import re

def list_all(directory):
    itemslist = os.listdir(directory)
    files = []
    for file in itemslist:
        path = os.path.abspath(os.path.join(directory, file))
        if os.path.isdir(path):
            files += list_all(path)
        else:
            files.append(path)

    return files


class Search(ttk.Frame):
    def __init__(self, parent: ttk.Panedwindow, path: str, opencommand: callable):
        super().__init__(parent)
        parent.forget(parent.panes()[0])
        self.pack(fill='both', expand=1)
        parent.insert('0', self)

        self.parent = parent
        self.path = path
        self.opencommand = opencommand
        self._style = ttkthemes.ThemedStyle()
        self._style.set_theme(get_theme())
        bg = self._style.lookup("TLabel", "background")
        fg = self._style.lookup("TLabel", "foreground")
        
        # Tkinter Variables
        self.case = tk.BooleanVar()
        self.regex = tk.BooleanVar()
        self.fullword = tk.BooleanVar()

        self.found = []
        ttk.Label(self, text="Search: ").pack(side="left",
                                                           anchor="nw",
                                                           fill="y")
        self.content = tk.Entry(
            self,
            background=darken_color(bg, 30, 30, 30),
            foreground=fg,
            insertbackground=fg,
            highlightthickness=0,
        )
        self.content.pack(side="left", fill="both")

        # Checkboxes
        self.case_yn = ttk.Checkbutton(self,
                                       text="Case Sensitive",
                                       variable=self.case)
        self.case_yn.pack(side="left")

        self.reg_yn = ttk.Checkbutton(self,
                                       text="RegExp",
                                       variable=self.regex)
        self.reg_yn.pack(side="left")

        self.fullw_yn = ttk.Checkbutton(self,
                                       text="Full Word",
                                       variable=self.fullword)
        self.fullw_yn.pack(side="left")
        
        for x in (self.case, self.regex, self.fullword):
            x.trace_add('write', self.find)
        self.content.bind("<KeyRelease>", self.find)
        
        self.content.insert('end', 'e')
        self.find()

    def re_search(self, pat, text, nocase=False, full_word=False, regex=False):
        if nocase and full_word:
            res = [(x[0], x[1]) for x in finditer_withlineno(
                r"\b" + re.escape(pat) +
                r"\b", text, (re.IGNORECASE, re.MULTILINE))]
        elif full_word:
            res = [(x[0], x[1]) for x in finditer_withlineno(
                r"\b" + re.escape(pat) + r"\b", text, re.MULTILINE)]
        elif nocase and regex:
            res = [(x[0], x[1]) for x in finditer_withlineno(
                pat, text, (re.IGNORECASE, re.MULTILINE))]
        elif regex:
            res = [(x[0], x[1]) for x in finditer_withlineno(
                pat, text, re.MULTILINE)]
        if nocase:
            res = [(x[0], x[1]) for x in find_all(pat, text, case=False)]
        else:
            res = [(x[0], x[1]) for x in find_all(pat, text)]
        return res

    def find(self, *_):
        path = self.path
        files = list_all(path)
        self.found.clear()
        s = self.content.get()
        
        if s:
            for file in files:
                with open(file) as f:
                    matchs = self.re_search(s,
                                            f.read(),
                                            nocase=not (self.case.get()),
                                            regex=self.regex.get())
                    if not matchs:
                        continue
                    for x in matches:
                        start = f'{x[0][0]}.{x[0][1]}'
                        end = f'{x[1][0]}.{x[1][1]}'
                        self.found.append([filename, start, end])
