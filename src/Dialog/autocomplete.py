import string

from src.Widgets.tktext import EnhancedText
from src.modules import ttk, tk

punc = [x for x in string.punctuation.replace('_', '')]
whites = [x for x in string.whitespace]


def sep_words(str_to_sep: str) -> list:
    result = str_to_sep
    for char in (*punc, *whites):
        result = result.replace(char, ' ')

    result = list(filter(None, result.split()))
    result = list(dict.fromkeys(result))
    return result
    

class CompleteDialog(ttk.Frame):
    def __init__(self, master: tk.Misc, text: [tk.Text, EnhancedText]):
        super().__init__(master, relief='groove')
        self.completions = ttk.Treeview(self, show='tree')
        self.completions.pack(side='left', fill='both', expand=True)
        self.completions.bind('<1>', self.complete)

        yscroll = ttk.Scrollbar(self, command=self.completions.yview)
        yscroll.pack(side='right', fill='y', expand=True)
        self.completions['yscrollcommand'] = yscroll.set
        self.text = text
        
        text.bind('<Button-1>', lambda _: self.place_forget())

    def complete(self, event: tk.Event = None) -> None:
        item = self.completions.identify("item", event.x, event.y)
        text = self.text
        completion = self.completions.item(item, 'text')
        text.delete(*self.index_word())
        text.insert('insert', completion)
        text.opts.key()

    def insert_completions(self) -> None:
        text = self.text
        dline = text.dlineinfo('insert')
        self.place_configure(x=dline[0] + dline[2], y=dline[1] + dline[3])
        content = text.get('1.0', 'end')
        all_matches = sep_words(content)

        curr_word = self.get_word()
        self.completions.delete(*self.completions.get_children())
        for match in all_matches:
            if curr_word in match:
                self.completions.insert('', 'end', text=match)

    def get_word(self) -> str:
        text = self.text
        try:
            return text.get(*self.index_word())
        except TypeError:
            pass

    def index_word(self) -> str:
        text = self.text
        try:
            content = text.get("1.0", "insert")
            words = sep_words(content)
            line = content.count('\n') + 1
            endcol = len(content.split('\n')[-1])
            startcol = endcol - len(words[-1])
            return f'{line}.{startcol}', f'{line}.{endcol}'
        except IndexError:
            pass
