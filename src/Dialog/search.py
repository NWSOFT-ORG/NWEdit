from src.Dialog.commondialog import get_theme
from src.functions import darken_color
from src.modules import tk, ttk, ttkthemes
import re


def finditer_withlineno(pattern, string, flags=0):
    """
    A version of 're.finditer' that returns '(match, line_number)' pairs.
    """

    matches = list(re.finditer(pattern, string, flags))
    if not matches:
        return []

    end = matches[-1].start()
    # -1 so a failed 'rfind' maps to the first line.
    newline_table = {-1: 0}
    for i, m in enumerate(re.finditer(r'\n', string), 1):
        # don't find newlines past our last match
        offset = m.start()
        if offset > end:
            break
        newline_table[offset] = i

    # Failing to find the newline is OK, -1 maps to 0.
    for m in matches:
        newline_offset = string.rfind('\n', 0, m.start())
        line_number = newline_table[newline_offset]
        yield ((line_number + 1, m.start() - newline_offset - 1),
               (line_number + 1, m.end() - newline_offset - 1))


def find_all(sub, string, case=True):
    start = 0
    if not case:
        sub = sub.lower()
        string = string.lower()
    while True:
        start = string.find(sub, start)
        if start == -1:
            return

        lines_ahead = string[:start].count('\n')
        newline_offset = string.rfind('\n', 0, start)
        end = start + len(sub)

        yield ((lines_ahead + 1, start - newline_offset - 1),
               (lines_ahead + 1, end - newline_offset - 1))
        start = end


class Search:
    def __init__(self, master: tk.Misc, text: tk.Text):
        self.master = master
        self.text = text
        self._style = ttkthemes.ThemedStyle()
        self._style.set_theme(get_theme())
        bg = self._style.lookup("TLabel", "background")
        fg = self._style.lookup("TLabel", "foreground")

        if self.text.searchable or self.text.navigate:
            return
        if not self.text.tag_ranges("sel"):
            self.start = "1.0"
            self.end = "end"
        self.starts = []
        self.search_frame = ttk.Frame(self.text.frame)
        
        # Tkinter Variables
        self.case = tk.BooleanVar()
        self.regex = tk.BooleanVar()
        self.fullword = tk.BooleanVar()

        self.search_frame.pack(anchor="nw", side="bottom")
        ttk.Label(self.search_frame, text="Search: ").pack(side="left",
                                                           anchor="nw",
                                                           fill="y")
        self.content = tk.Entry(
            self.search_frame,
            background=darken_color(bg, 30, 30, 30),
            foreground=fg,
            insertbackground=fg,
            highlightthickness=0,
        )
        self.content.pack(side="left", fill="both")

        self.forward = ttk.Button(self.search_frame, text="<", width=1)
        self.forward.pack(side="left")

        self.backward = ttk.Button(self.search_frame, text=">", width=1)
        self.backward.pack(side="left")

        ttk.Label(self.search_frame, text="Replacement: ").pack(side="left",
                                                                anchor="nw",
                                                                fill="y")
        self.repl = tk.Entry(
            self.search_frame,
            background=darken_color(bg, 30, 30, 30),
            foreground=fg,
            insertbackground=fg,
            highlightthickness=0,
        )
        self.repl.pack(side="left", fill="both")

        self.repl_button = ttk.Button(self.search_frame, text="Replace all")
        self.repl_button.pack(side="left")
        self.clear_button = ttk.Button(self.search_frame, text="Clear All")
        self.clear_button.pack(side="left")

        # Checkboxes
        self.case_yn = ttk.Checkbutton(self.search_frame,
                                       text="Case Sensitive",
                                       variable=self.case)
        self.case_yn.pack(side="left")

        self.reg_yn = ttk.Checkbutton(self.search_frame,
                                       text="RegExp",
                                       variable=self.regex)
        self.reg_yn.pack(side="left")

        self.fullw_yn = ttk.Checkbutton(self.search_frame,
                                       text="Full Word",
                                       variable=self.fullword)
        self.fullw_yn.pack(side="left")
        
        for x in (self.case, self.regex, self.fullword):
            x.trace_add('write', self.find)

        self.clear_button.config(command=self.clear)
        self.repl_button.config(command=self.replace)
        self.forward.config(command=self.nav_forward)
        self.backward.config(command=self.nav_backward)
        self.content.bind("<KeyRelease>", self.find)
        ttk.Button(self.search_frame, text="x",
                   command=self._exit).pack(side="right")
        self.text.searchable = True
        
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
        text = self.text
        text.tag_remove("found", "1.0", "end")
        s = self.content.get()
        self.starts.clear()
        if s:
            matches = self.re_search(s,
                                     text.get('1.0', 'end'),
                                     nocase=not (self.case.get()),
                                     regex=self.regex.get())
            for x in matches:
                start = f'{x[0][0]}.{x[0][1]}'
                end = f'{x[1][0]}.{x[1][1]}'
                self.starts.append(start)
                text.tag_add("found", start, end)
            text.tag_config("found", foreground="red", background="yellow")

    def replace(self):
        text = self.text
        text.tag_remove("found", "1.0", "end")
        s = self.content.get()
        r = self.repl.get()
        if s:
            matches = self.re_search(s,
                                     text.get('1.0', 'end'),
                                     nocase=not (self.case.get()),
                                     regex=self.regex.get())
            for x in matches:
                start = f'{x[0][0]}.{x[0][1]}'
                end = f'{x[1][0]}.{x[1][1]}'
                text.delete(start, end)
                text.insert(start, r)

    def clear(self):
        text = self.text
        text.tag_remove("found", "1.0", "end")

    def nav_forward(self):
        try:
            text = self.text
            curpos = text.index("insert")
            if curpos in self.starts:
                prev = self.starts.index(curpos) - 1
                text.mark_set("insert", self.starts[prev])
                text.see("insert")
        except Exception:
            pass

    def nav_backward(self):
        try:
            text = self.text
            curpos = text.index("insert")
            if curpos in self.starts:
                prev = self.starts.index(curpos) + 1
                text.mark_set("insert", self.starts[prev])
                text.see("insert")
        except Exception:
            pass

    def _exit(self):
        self.text.searchable = False
        self.search_frame.pack_forget()
        self.clear()
        self.text.focus_set()
