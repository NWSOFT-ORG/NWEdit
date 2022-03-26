from src.modules import tk, ttk, art, sys, io
from src.Widgets.winframe import WinFrame


def listfonts():
    # A lot of string operations and some stdout magic
    old_stdout = sys.stdout  # Memorize the default stdout stream
    sys.stdout = buffer = io.StringIO()

    art.font_list('Test', 'ascii')
    sys.stdout = old_stdout  # Put the old stream back in place
    fonts = buffer.getvalue().split('\n\n')

    for index, item in enumerate(fonts):
        fonts[index] = item.split('\n')[0][:-3]
        # Each font is name(spc):(spc), so minus three chars
    return fonts[:-1]
    # Last one is '', which is useless.


class StyleWindow(WinFrame):
    def __init__(self, master, text, handler):
        super().__init__(master, 'Insert Ascii Art')

        self.text = text

        self.entry = tk.Entry(self)
        self.entry.pack(fill='x')
        self.entry.insert('end', 'Hello, World')

        self.font_var = tk.StringVar()

        self.font = ttk.Combobox(self, state='readonly', values=listfonts(), textvariable=self.font_var)
        self.font.set(listfonts()[0])
        self.font.pack(fill='x')

        self.preview = tk.Text(self, state='disabled', wrap='none')
        self.preview.pack(fill='both')

        ttk.Button(self, text='Insert >>', command=self.insert).pack(fill='x')

        self.entry.bind('<KeyRelease>', self.update_text)
        self.font_var.trace_add('write', self.update_text)
        self.update_text()

    def update_text(self, *_):
        self.preview.config(state='normal')
        self.preview.delete('1.0', 'end')
        ascii_text = ""
        try:
            ascii_text = art.text2art(self.entry.get(), font=self.font.get(), chr_ignore=False)
        except art.artError:
            ascii_text = art.text2art(self.entry.get(), font=self.font.get(), chr_ignore=True)
        finally:
            self.preview.insert('end', ascii_text)
            self.preview.config(state='disabled')

    def insert(self):
        self.text.insert('insert', self.preview.get('1.0', 'end'))
        self.destroy()
