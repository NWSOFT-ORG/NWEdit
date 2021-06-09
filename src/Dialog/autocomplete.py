import string
from src.modules import ttk

def sep_words(str_to_sep: str) -> list:
    result = str_to_sep
    punc = [x for x in string.punctuation]
    whites = [x for x in string.whitespace]
    for char in (*punc, *whites):
        result = result.replace(char, ' ')

    result = list(filter(None, result.split()))
    result = dict.fromkeys(result)
    return result
    

class CompleteDialog(ttk.Frame):
    def __init__(self, master, text):
        super().__init__(master, relief='groove')
        self.completions = ttk.Treeview(self, show='tree')
        self.completions.pack(side='left',fill='both', expand=1)
        self.completions.bind('<1>', self.click_treeview)

        yscroll = ttk.Scrollbar(self, command=self.completions.yview)
        yscroll.pack(side='right', fill='y', expand=1)
        self.completions['yscrollcommand'] = yscroll.set
        self.text = text

    def click_treeview(self, _=None):
        item = self.completions.focus()
        text = self.text
        completion = self.completions.item(item, 'text')
        text.insert('insert', completion)

    def complete(self, _=None):
        text = self.text
        dline = text.dlineinfo('insert')
        self.place_configure(x=dline[0] + dline[2], y=dline[1] + dline[3])
        content = text.get('1.0', 'insert')
        all_matches = sep_words(content)

        self.completions.delete(*self.completions.get_children())
        for match in all_matches:
            self.completions.insert('', 'end', text=match)