import string
from typing import *
from typing import Tuple

from src.modules import tk, ttk
from src.types import Tk_Widget
from src.Widgets.scrollbar import Scrollbar

punc = [x for x in string.punctuation.replace("_", "")]
whites = [x for x in string.whitespace]


def sort(words):
    # Time: 0.8s
    _words = {words[x]: 0 for x in range(len(words))}

    for word in _words:
        _words[word] = words.count(word)

    words.sort(key=lambda word: _words[word])
    return words


def sep_words(str_to_sep: str) -> list:
    result = str_to_sep
    for char in (*punc, *whites):
        result = result.replace(char, " ")

    result = result.split()
    result = sort(result)
    result = list(filter(None, result))
    result = list(dict.fromkeys(result))
    return result


class CompleteDialog(ttk.Frame):
    def __init__(self, master: Tk_Widget, text: tk.Text, key: Callable):
        super().__init__(master, relief="groove")
        self.key = key

        self.completions = ttk.Treeview(self, show="tree")
        self.completions.pack(side="left", fill="both", expand=1)
        self.completions.bind("<1>", self.complete)

        yscroll = Scrollbar(self, command=self.completions.yview)
        yscroll.pack(side="right", fill="y", expand=1)
        self.completions["yscrollcommand"] = yscroll.set
        self.text = text

        text.bind("<Button-1>", lambda _: self.place_forget(), add=True)
        text.bind("<Key>", lambda _: self.place_forget(), add=True)

    def complete(self, event: tk.Event = None):
        item = self.completions.identify("item", event.x, event.y)
        text = self.text
        completion = self.completions.item(item, "text")
        text.delete(*self.index_word)
        text.insert("insert", completion)
        self.key()

    def insert_completions(self):
        text = self.text
        content = text.get("1.0", "end")
        all_matches = sep_words(content)
        if not all_matches:
            self.place_forget()
            return

        dline = text.dlineinfo("insert")
        self.place_configure(x=dline[0] + dline[2], y=dline[1] + dline[3])

        curr_word = self.get_word
        self.completions.delete(*self.completions.get_children())
        for match in all_matches:
            if curr_word in match and curr_word != match:
                self.completions.insert("", "end", text=match)

    @property
    def get_word(self) -> Union[str, None]:
        text = self.text
        try:
            return text.get(*self.index_word)
        except TypeError:
            return None

    @property
    def index_word(self) -> Tuple[str, str] | None:
        text = self.text
        try:
            content = text.get("1.0", "insert")
            words = sep_words(content)
            line = content.count("\n") + 1
            endcol = len(content.split("\n")[-1])
            startcol = endcol - len(words[-1])
            return f"{line}.{startcol}", f"{line}.{endcol}"
        except IndexError:
            return None
