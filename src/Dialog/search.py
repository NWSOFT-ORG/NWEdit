import re
from tokenize import Number
from typing import *

from src.modules import tk, ttk
from src.Utils.images import get_image
from src.Widgets.tkentry import Entry
from src.Widgets.tktext import EnhancedText


def finditer_withlineno(
    pattern, string, flags: Union[re.RegexFlag, int] = 0
) -> Iterable[Tuple[int]]:
    """
    A version of re.finditer that returns '(match, line_number)' pairs.
    """

    matches = list(re.finditer(pattern, string, flags))
    if not matches:
        return []

    end = matches[-1].start()
    # -1 so a failed 'rfind' maps to the first line.
    newline_table = {-1: 0}
    for i, m in enumerate(re.finditer(r"\n", string), 1):
        # don't find newlines past the last match
        offset = m.start()
        if offset > end:
            break
        newline_table[offset] = i

    # Failing to find the newline is OK,–1 maps to 0.
    for m in matches:
        newline_offset = string.rfind("\n", 0, m.start())
        line_number = newline_table[newline_offset]
        yield (
            (line_number + 1, m.start() - newline_offset - 1),
            (line_number + 1, m.end() - newline_offset - 1),
        )


def find_all(sub: Text, string: Text, case: bool = True) -> Iterable[Tuple[int]]:
    start = 0
    if not case:
        sub = sub.lower()
        string = string.lower()
    while True:
        start = string.find(sub, start)
        if start == -1:
            return

        lines_ahead = string[:start].count("\n")
        newline_offset = string.rfind("\n", 0, start)
        end = start + len(sub)

        yield (
            (lines_ahead + 1, start - newline_offset - 1),
            (lines_ahead + 1, end - newline_offset - 1),
        )
        start = end


def re_search(
    pat: Text,
    text: Text,
    nocase: bool = False,
    full_word: bool = False,
    regex: bool = False,
) -> List:
    if nocase and full_word:
        res = [
            (x[0], x[1])
            for x in finditer_withlineno(
                r"\b" + re.escape(pat) + r"\b", text, (re.IGNORECASE | re.MULTILINE)
            )
        ]
    elif full_word:
        res = [
            (x[0], x[1])
            for x in finditer_withlineno(
                r"\b" + re.escape(pat) + r"\b", text, re.MULTILINE
            )
        ]
    elif nocase and regex:
        res = [
            (x[0], x[1])
            for x in finditer_withlineno(pat, text, (re.IGNORECASE | re.MULTILINE))
        ]
    elif regex:
        res = [(x[0], x[1]) for x in finditer_withlineno(pat, text, re.MULTILINE)]
    elif nocase:
        res = [(x[0], x[1]) for x in find_all(pat, text, case=False)]
    else:
        res = [(x[0], x[1]) for x in find_all(pat, text)]
    return res


class Search:
    def __init__(self, master: ttk.Notebook, text: EnhancedText) -> None:
        self.master = master
        self.text = text
        self._style = ttk.Style()
        bg = self._style.lookup("TLabel", "background")

        if self.text.search or self.text.navigate:
            return
        if not self.text.tag_ranges("sel"):
            self.start = "1.0"
            self.end = "end"
        self.starts = []
        self.main_frame = ttk.Frame(self.master, takefocus=True)
        self.search_frame = ttk.Frame(self.main_frame)

        # Tkinter Variables
        self.case = tk.BooleanVar()
        self.regex = tk.BooleanVar()
        self.fullword = tk.BooleanVar()

        ttk.Label(self.search_frame, text="Search for:").pack(
            side="left", anchor="nw", fill="y"
        )
        self.content = Entry(self.search_frame)
        self.content.pack(side="left", fill="both")

        self.forward = ttk.Button(
            self.search_frame,
            image=get_image("prev-tab"),
            width=1,
            takefocus=False,
            command=self.nav_forward,
        )
        self.forward.pack(side="left")

        self.backward = ttk.Button(
            self.search_frame,
            image=get_image("next-tab"),
            width=1,
            takefocus=False,
            command=self.nav_forward,
        )
        self.backward.pack(side="left")

        self.replace_frame = ttk.Frame(self.main_frame)
        self.replace_frame.pack(side="bottom", anchor="nw")
        self.search_frame.pack(anchor="nw", side="bottom")

        ttk.Label(self.replace_frame, text="Replace with:").pack(
            side="left", anchor="nw", fill="y"
        )
        self.replace_with = Entry(self.replace_frame)
        self.replace_with.pack(side="left", fill="both")

        self.replace_all_button = ttk.Button(
            self.replace_frame,
            text="Replace All",
            takefocus=False,
            command=self.replace_all,
        )
        self.replace_all_button.pack(side="left")
        self.clear_button = ttk.Button(
            self.replace_frame, text="Clear All", takefocus=False, command=self.clear
        )
        self.clear_button.pack(side="left")

        # Checkboxes
        self.case_yn = ttk.Checkbutton(
            self.search_frame, text="Case Sensitive", variable=self.case
        )
        self.case_yn.pack(side="left")

        self.reg_yn = ttk.Checkbutton(
            self.search_frame, text="RegExp", variable=self.regex
        )
        self.reg_yn.pack(side="left")

        self.fullw_yn = ttk.Checkbutton(
            self.search_frame, text="Full Word", variable=self.fullword
        )
        self.fullw_yn.pack(side="left")

        for variable in (self.case, self.regex, self.fullword):
            variable.trace_add("write", self.find)

        self.content.bind("<KeyRelease>", self.find)
        ttk.Button(self.main_frame, image=get_image("close"), command=self._exit).pack(
            side="right", anchor="se"
        )
        self.text.search = True

        self.text.bind("<Escape>", self._exit)
        self.main_frame.bind("<Escape>", self._exit)

        self.master.add(self.main_frame, text="Search")

    def find(self, *_) -> None:
        text = self.text
        text.tag_remove("found", "1.0", "end")
        s = self.content.get()
        self.starts.clear()
        if s:
            matches = re_search(
                s,
                text.get("1.0", "end"),
                nocase=not (self.case.get()),
                regex=self.regex.get(),
            )
            for x in matches:
                start = f"{x[0][0]}.{x[0][1]}"
                end = f"{x[1][0]}.{x[1][1]}"
                self.starts.append(start)
                text.tag_add("found", start, end)
            text.tag_config("found", foreground="red", background="yellow")

    def replace_all(self) -> None:
        text = self.text
        r = self.replace_with.get()
        self.find()

        ranges = iter(self.text.tag_ranges("found"))
        for match_index in ranges:
            # The try...except statement for StopIteration isn't required, because tag_ranges() returns paired indexes
            text.delete(match_index, next(ranges))
            text.insert(match_index, r)

    def replace_this(self) -> None:
        text = self.text
        r = self.replace_with.get()
        self.find()

        current_location = float(text.index("insert"))

        ranges = iter(self.text.tag_ranges("found"))
        for match_index in ranges:
            # The try...except statement for StopIteration isn't required, because tag_ranges() returns paired indexes
            next_index = next(ranges)
            if next_index <= current_location <= match_index:
                text.delete(match_index, next(ranges))
                text.insert(match_index, r)

    def clear(self) -> None:
        text = self.text
        text.tag_remove("found", "1.0", "end")

    def nav_forward(self) -> None:
        try:
            text = self.text
            curpos = text.index("insert")
            if curpos in self.starts:
                prev = self.starts.index(curpos) + 1
            else:
                prev = 0
            text.mark_set("insert", self.starts[prev])
            text.see("insert")
        except tk.TclError:
            pass

    def nav_backward(self) -> None:
        try:
            text = self.text
            curpos = text.index("insert")
            if curpos in self.starts:
                prev = self.starts.index(curpos) - 1
            else:
                prev = -1
            text.mark_set("insert", self.starts[prev])
            text.see("insert")
        except tk.TclError:
            pass

    def _exit(self, _=None) -> None:
        self.text.unbind("<Escape>")
        self.main_frame.unbind("<Escape>")
        self.text.search = False
        self.master.forget(self.master.index("current"))
        self.clear()
        self.text.focus_set()
