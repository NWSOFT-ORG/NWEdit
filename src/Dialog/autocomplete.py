import string
from src.modules import ttk

def sep_words(str_to_sep: str) -> list:
    result = str_to_sep
    punc = [x for x in string.punctuation]
    whites = [x for x in string.whitespace]
    for char in (*punc, *whites):
        result = result.replace(char, ' ')

    return list(filter(None, result.split()))
    

class CompleteDialog(ttk.Frame):
    def __init__(self, master, text):
        super.__init__(master, relief='groove')
        self.text = text
        self.text.event_add('<<Complete>>', '<KeyRelease>')
        self.text.bind('<<Complete>>', self.complete)
    
    def complete(self, _=None):
        # TODO: Use dlineinfo to get y and x
        self.place_forget()
        text = self.text
        content = text.get('1.0', 'insert')
        all_matches = sep_words(content)
        self.place()