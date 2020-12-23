import os
import tkinter as tk
import tkinter.ttk as ttk
from ttkthemes import ThemedStyle
from hashlib import md5
import tkinter.filedialog
import tkinter.messagebox
import ttkthemes
import sys
from tkinter import TclError
from tkinter import font as tkfont
from tkinter import scrolledtext
import pygments
from pygments.lexers import PythonLexer

_PLTFRM = (True if sys.platform.startswith('win') else False)
_BATCH_BUILD = ('''
@echo off

title Build Results

measure.py start

echo.

echo.

echo ----------------------------------------------------

python3 %s

echo Program Finished With Exit Code %ERRORLEVEL%

measure.py stop

echo ----------------------------------------------------

echo.

pause
''' if _PLTFRM else '''
#!/bin/bash

set +v

mytitle="Build Results"

# Require ASNI Escape Code support

python3 ./measure.py start

echo -e '\033k'$mytitle'\033\\'

echo ===================================================

python3 %s

echo Program Finished With Exit Code $?

python3 ./measure.py stop

echo ===================================================

echo Exit in 10 secs...

sleep 10s
''')


class TextLineNumbers(tk.Canvas):
    def __init__(self, *args, **kwargs):
        tk.Canvas.__init__(self, *args, **kwargs)
        self.textwidget = None

    def attach(self, text_widget):
        self.textwidget = text_widget

    def redraw(self, *args):
        '''redraw line numbers'''
        self.delete("all")

        i = self.textwidget.index("@0,0")
        w = len(self.textwidget.index("end-1c linestart"))
        self.config(width=w * 10)
        while True:
            dline = self.textwidget.dlineinfo(i)
            if dline is None:
                break
            y = dline[1]
            linenum = str(i).split(".")[0]
            self.create_text(2, y, anchor="nw", text=linenum,
                             fill='black', font=self.textwidget['font'])
            i = self.textwidget.index("%s+1line" % i)


class CustomText(tk.Text):
    def __init__(self, *args, **kwargs):
        tk.scrolledtext.ScrolledText.__init__(self, *args, **kwargs)

        # create a proxy for the underlying widget
        self._orig = self._w + "_orig"
        self.tk.call("rename", self._w, self._orig)
        self.tk.createcommand(self._w, self._proxy)

    def _proxy(self, *args):
        try:
            # The text widget might throw an error while pasting text!
            # let the actual widget perform the requested action
            cmd = (self._orig,) + args
            result = self.tk.call(cmd)

            # generate an event if something was added or deleted,
            # or the cursor position changed
            if (args[0] in ("insert", "replace", "delete") or
                    args[0:3] == ("mark", "set", "insert") or
                    args[0:2] == ("xview", "moveto") or
                    args[0:2] == ("xview", "scroll") or
                    args[0:2] == ("yview", "moveto") or
                    args[0:2] == ("yview", "scroll")
                    ):
                self.event_generate("<<Change>>", when="tail")

            # return what the actual widget returned
            return result
        except:
            pass


class EnhancedTextFrame(ttk.Frame):
    def __init__(self, *args, **kwargs):
        ttk.Frame.__init__(self, *args, **kwargs)
        self.text = CustomText(self, bg='black', fg='white', insertbackground='white',
                               selectforeground='black', selectbackground='white', highlightthickness=0,
                               font='Menlo 13')
        self.linenumbers = TextLineNumbers(
            self, width=30, bg='darkgray', bd=0, highlightthickness=0)
        self.linenumbers.attach(self.text)
        self.linenumbers.pack(side="left", fill="y")
        self.text.pack(side="right", fill="both", expand=True)

        self.text.bind("<<Change>>", self._on_change)
        self.text.bind("<Configure>", self._on_change)

    def _on_change(self, event):
        self.linenumbers.redraw()


class CustomNotebook(ttk.Notebook):
    """A ttk Notebook with close buttons on each tab"""

    __initialized = False

    def __init__(self, master, cmd):
        if not self.__initialized:
            self.__initialize_custom_style()
            self.__inititialized = True
        ttk.Notebook.__init__(self, master=master, style='CustomNotebook')
        self.cmd = cmd

        self._active = None

        self.bind("<ButtonPress-1>", self.on_close_press, True)
        self.bind("<ButtonRelease-1>", self.on_close_release)

    def on_close_press(self, event):
        """Called when the button is pressed over the close button"""

        element = self.identify(event.x, event.y)

        if "close" in element:
            index = self.index("@%d,%d" % (event.x, event.y))
            self.state(['pressed'])
            self._active = index

    def on_close_release(self, event):
        try:
            """Called when the button is released over the close button"""
            if not self.instate(['pressed']):
                return

            element = self.identify(event.x, event.y)
            index = self.index("@%d,%d" % (event.x, event.y))

            if "close" in element and self._active == index:
                self.cmd()

            self.state(["!pressed"])
            self._active = None
        except:
            pass

    def __initialize_custom_style(self):
        style = ttk.Style()
        self.images = (
            tk.PhotoImage("img_close", data='''iVBORw0KGgoAAAANSUhEUgAAACAAAAAgA
            gMAAAAOFJJnAAAAAXNSR0IB2cksfwAAAAlwSFlzAAALEwAACxMBAJqcGAAAAAxQTFRFA
            AAAAAAA/yYA////nxJg7AAAAAR0Uk5TAP///7MtQIgAAACMSURBVHicPZC9AQMhCIVJk
            yEyTZbIEnfLZIhrTgtHYB9HoIB7/CiFfArCA6JfGNGrhX3pnfCnT3i+6BQHu+lU+O5gg
            KE3HTaRIgBGkk3AUKQ0AE4wAO+IOrDwDBiKCg7dNKGZFPCCFepWyfg1Vx2pytkCvbIpr
            inDq4QwV5hSS/yhNc4ecI+8l7DW8gDYFaqpCCFJsQAAAABJRU5ErkJggg==
                '''),
            tk.PhotoImage("img_closeactive", data='''iVBORw0KGgoAAAANSUhEUgAAACA
            AAAAgBAMAAACBVGfHAAAAAXNSR0IB2cksfwAAAAlwSFlzAAALEwAACxMBAJqcGAAAAA9
            QTFRFAAAAAAAA/YAI////////uHhEXgAAAAV0Uk5TAP///zOOAqjJAAAAk0lEQVR4nGW
            S2RGAMAhE44wFaDow6SD035scCwMJHxofyxGwtfYma2zXSPYw6Bl8VTCJJZ2fbkQsYbB
            CAEAhWAL07QIFLlGHAEiMK7CjYQV6RqAB+UB1AyJBZgCWoDYAS2gUMHewh0iOklSrpLL
            WR2pMval1c6bLITyu7z3EgLyFNMI65BFTtzUcizpWeS77rr/DDzkRRQdj40f8AAAAAEl
            FTkSuQmCC
                '''),
            tk.PhotoImage("img_closepressed", data='''iVBORw0KGgoAAAANSUhEUgAAAC
            AAAAAgAgMAAAAOFJJnAAAAAXNSR0IB2cksfwAAAAlwSFlzAAALEwAACxMBAJqcGAAAAA
            xQTFRFAAAAAAAA//8K////dEqdoAAAAAR0Uk5TAP///7MtQIgAAACMSURBVHicPZC9AQ
            MhCIVJkyEyTZbIEnfLZIhrTgtHYB9HoIB7/CiFfArCA6JfGNGrhX3pnfCnT3i+6BQHu+
            lU+O5ggKE3HTaRIgBGkk3AUKQ0AE4wAO+IOrDwDBiKCg7dNKGZFPCCFepWyfg1Vx2pyt
            kCvbIprinDq4QwV5hSS/yhNc4ecI+8l7DW8gDYFaqpCCFJsQAAAABJRU5ErkJggg==
            ''')
        )

        style.element_create(
            "close",
            "image",
            "img_close", ("active", "pressed",
                          "!disabled", "img_closepressed"),
            ("active", "!disabled", "img_closeactive"),
            border=8,
            sticky='')
        style.layout("CustomNotebook", [("CustomNotebook.client", {
            "sticky": "nswe"
        })])
        style.layout("CustomNotebook.Tab", [("CustomNotebook.tab", {
            "sticky":
            "nswe",
            "children": [("CustomNotebook.padding", {
                "side":
                "top",
                "sticky":
                "nswe",
                "children": [("CustomNotebook.focus", {
                    "side":
                    "top",
                    "sticky":
                    "nswe",
                    "children": [
                        ("CustomNotebook.label", {
                            "side": "left",
                            "sticky": ''
                        }),
                        ("CustomNotebook.close", {
                            "side": "left",
                            "sticky": ''
                        }),
                    ]
                })]
            })]
        })])


class Document:
    def __init__(self, Frame, TextWidget, FileDir=''):
        self.file_dir = FileDir
        self.fulldir = FileDir
        self.file_name = 'Untitled.py' if not FileDir else os.path.basename(
            FileDir)
        self.textbox = TextWidget


class Editor:
    def __init__(self, master):
        # TODO: Add a tab click event!
        self.master = master
        style = ThemedStyle(self.master)
        style.set_theme("black")
        self.count = 0
        self.master.geometry("600x400")
        self.master.title('PyEdit +')
        self.master.iconphoto(True, tk.PhotoImage(data='''iVBORw0KGgoAAAANSUhEU
        gAAACAAAAAgBAMAAACBVGfHAAAAAXNSR0IB2cksfwAAAAlwSFlzAAASdAAAEnQB3mYfeAAA
        ABJQTFRFAAAAAAAA////TWyK////////WaqEwgAAAAZ0Uk5TAP8U/yr/h0gXnQAAAHpJREF
        UeJyNktENgCAMROsGog7ACqbpvzs07L+KFCKWFg0XQtLHFQIHAEBoiiAK2BSkXlBpzWDX4D
        QGsRhw9B3SMwNSSj1glNEDqhUpUGw/gMuUd+d2Csny6xgAZB4A1IDwG1SxAc/95t7DAPPIm
        4/BBeWjdGHr73AB3CCCXSvLODzvAAAAAElFTkSuQmCC'''))

        with open('settings.txt') as f:
            self.settings = f.read()

        self.filetypes = eval(self.settings.split('\n')[4][6:])

        self.tabs = {}

        self.nb = CustomNotebook(master, self.close_tab)
        self.nb.bind('<B1-Motion>', self.move_tab)
        self.nb.event_add("<<TabClick>>", "<Button-1>")
        self.nb.bind("<<TabClick>>", self.settitle)
        self.nb.pack(expand=1, fill='both')
        self.nb.enable_traversal()

        self.master.protocol('WM_DELETE_WINDOW', self.exit)

        self.master.bind('<Command-o>', self.open_file)
        self.master.bind('<Control-n>', self.new_file)

        menubar = tk.Menu(self.master)

        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label='New Tab', command=self.new_file)
        filemenu.add_command(label='Open File', command=self.open_file)
        filemenu.add_command(label='Save File', command=self.save_file)
        filemenu.add_command(label='Save As...', command=self.save_as)
        filemenu.add_command(label='Close Tab', command=self.close_tab)
        filemenu.add_separator()
        filemenu.add_command(label='Exit Editor', command=self.exit)

        editmenu = tk.Menu(menubar, tearoff=0)
        editmenu.add_command(label='Undo', command=self.undo)
        editmenu.add_command(label='Redo', command=self.redo)
        editmenu.add_separator()
        editmenu.add_command(label='Cut', command=self.cut)
        editmenu.add_command(label='Copy', command=self.copy)
        editmenu.add_command(label='Paste', command=self.paste)
        editmenu.add_command(label='Delete', command=self.delete)
        editmenu.add_command(label='Select All', command=self.select_all)

        codemenu = tk.Menu(menubar, tearoff=0)
        codemenu.add_command(label='Build', command=self.build)
        codemenu.add_command(label='Search', command=self.search)

        helpmenu = tk.Menu(menubar, tearoff=0)
        helpmenu.add_command(label='Version', command=self.version)

        menubar.add_cascade(label='File', menu=filemenu)
        menubar.add_cascade(label='Edit', menu=editmenu)
        menubar.add_cascade(label='Code', menu=codemenu)
        menubar.add_cascade(label='Help', menu=helpmenu)
        self.master.config(menu=menubar)

        self.right_click_menu = tk.Menu(self.master, tearoff=0)
        self.right_click_menu.add_command(label='Undo', command=self.undo)
        self.right_click_menu.add_command(label='Redo', command=self.redo)
        self.right_click_menu.add_separator()
        self.right_click_menu.add_command(label='Cut', command=self.cut)
        self.right_click_menu.add_command(label='Copy', command=self.copy)
        self.right_click_menu.add_command(label='Paste', command=self.paste)
        self.right_click_menu.add_command(label='Delete', command=self.delete)
        self.right_click_menu.add_separator()
        self.right_click_menu.add_command(
            label='Select All', command=self.select_all)

        self.tab_right_click_menu = tk.Menu(self.master, tearoff=0)
        self.tab_right_click_menu.add_command(
            label='New Tab', command=self.new_file)
        self.tab_right_click_menu.add_command(
            label='Close Tab', command=self.close_tab)
        self.nb.bind('<Button-3>', self.right_click_tab)
        first_tab = ttk.Frame(self.nb)
        self.tabs[first_tab] = Document(
            first_tab, self.create_text_widget(first_tab))
        self.nb.add(first_tab, text='Untitled.py   ')

        def tab(event):
            self.tabs[self.get_tab()].textbox.insert('insert', ' ' * 4)
            return 'break'

        self.master.bind('<Control-s>', self.save_file)
        self.master.bind('<Control-w>', self.close_tab)
        self.master.bind('<Button-3>', self.right_click)
        self.master.bind('<Control-z>', self.undo)
        self.master.bind('<Control-Z>', self.redo)
        self.master.bind('<Control-b>', self.build)
        self.master.bind('<Control-f>', self.search)
        self.master.bind('<Tab>', tab)
        for x in ['"', "'", '(', '[', '{']:
            self.master.bind(x, self.autoinsert)

    def settitle(self, event=None):
        print('hi')
        self.master.title(f'PyEdit+ - {self.nb.tab(self.nb.select(), "text")}')

    def create_text_widget(self, frame):
        textframe = EnhancedTextFrame(frame)
        textframe.pack(fill='both', expand=1)

        textbox = textframe.text
        textbox.frame = frame
        textbox.tag_configure('Token.Keyword', foreground='#8cc4ff')
        textbox.tag_configure('Token.Name.Builtin.Pseudo',
                              foreground='#ad7fa8')
        textbox.tag_configure(
            'Token.Literal.Number.Integer', foreground='#008000')
        textbox.tag_configure(
            'Token.Literal.Number.Float', foreground='#008000')
        textbox.tag_configure(
            'Token.Literal.String.Single', foreground='#b77600')
        textbox.tag_configure(
            'Token.Literal.String.Double', foreground='#b77600')
        textbox.tag_configure('Token.Literal.String.Doc', foreground='#b77600')
        textbox.tag_configure('Token.Comment.Single', foreground='#73d216')
        textbox.tag_configure('Token.Comment.Hashbang', foreground='#73d216')
        textbox.bind('<Return>', self.autoindent)
        textbox.bind("<<set-line-and-column>>", self.key)
        textbox.event_add("<<set-line-and-column>>", "<KeyRelease>",
                          "<ButtonRelease>")
        textbox.statusbar = ttk.Label(
            frame, text='PyEdit +', justify='right', anchor='e')
        textbox.statusbar.pack(side='bottom', fill='x', anchor='e')

        self.master.geometry('1000x600')

        textbox.edited = False
        textbox.focus_set()
        return textbox

    def key(self, event=None, ismouse=False):
        currtext = self.tabs[self.get_tab()].textbox
        try:
            self._highlight_text()
            currtext.edited = True
            self._highlight_text()
            currtext.statusbar.config(text=f"PyEdit+ | file {self.nb.tab(self.get_tab())['text']}| ln {int(float(currtext.index('insert')))} | col {str(int(currtext.index('insert').split('.')[1:][0]))}")
        except:
            currtext.statusbar.config(text='PyEdit +')

    def _highlight_text(self):
        '''Highlight the text in the text box.'''

        start_index = self.tabs[self.get_tab()].textbox.index('@0,0')
        end_index = self.tabs[self.get_tab()].textbox.index(tk.END)

        for tag in self.tabs[self.get_tab()].textbox.tag_names():
            if tag == 'sel':
                continue
            self.tabs[self.get_tab()].textbox.tag_remove(
                tag, self.tabs[self.get_tab()].textbox.index('@0,0'), end_index)

        code = self.tabs[self.get_tab()].textbox.get(start_index, end_index)

        for index, line in enumerate(code):
            if index == 0 and line != '\n':
                break
            elif line == '\n':
                start_index = self.tabs[self.get_tab()].textbox.index(f'{start_index}+1line')
            else:
                break

        self.tabs[self.get_tab()].textbox.mark_set('range_start', start_index)
        for token, content in pygments.lex(code, PythonLexer()):
            self.tabs[self.get_tab()].textbox.mark_set('range_end', f'range_start + {len(content)}c')
            self.tabs[self.get_tab()].textbox.tag_add(
                str(token), 'range_start', 'range_end')
            self.tabs[self.get_tab()].textbox.mark_set(
                'range_start', 'range_end')

    def open_file(self, file=''):

        if not file:
            file_dir = (tkinter.filedialog.askopenfilename(
                master=self.master, initialdir='/', title='Select file', filetypes=self.filetypes))
        else:
            file_dir = file

        if file_dir:
            try:
                file = open(file_dir)

                new_tab = ttk.Frame(self.nb)
                self.tabs[new_tab] = Document(new_tab,
                                              self.create_text_widget(new_tab), file_dir)
                self.nb.add(new_tab, text=os.path.basename(file_dir) + ' ' * 3)
                self.nb.select(new_tab)

                # Puts the contents of the file into the text widget.
                self.tabs[new_tab].textbox.insert('end',
                                                  file.read().replace('\t', ' ' * 4))
                self.tabs[new_tab].textbox.focus_set()
                self.tabs[new_tab].textbox.edited = True
                self.key()
            except:
                return

    def save_as(self):
        if len(self.tabs) > 0:
            curr_tab = self.get_tab()
            file_dir = (tkinter.filedialog.asksaveasfilename(
                master=self.master,
                initialdir='/',
                title='Save As...',
                filetypes=self.filetypes,
                defaultextension='.py'))
            if not file_dir:
                return

            self.tabs[curr_tab].file_dir = file_dir
            self.tabs[curr_tab].file_name = os.path.basename(file_dir)
            self.nb.tab(curr_tab, text=self.tabs[curr_tab].file_name)
            file = open(file_dir, 'w')
            file.write(self.tabs[curr_tab].textbox.get(1.0, 'end'))
            file.close()

    def save_file(self, *args):
        try:
            curr_tab = self.get_tab()
            if not self.tabs[curr_tab].file_dir:
                self.save_as()
            else:
                with open(self.tabs[curr_tab].file_dir) as file:
                    file.write(self.tabs[curr_tab].textbox.get(1.0, 'end'))
        except:
            pass

    def new_file(self, *args):
        new_tab = ttk.Frame(self.nb)
        self.tabs[new_tab] = Document(
            new_tab, self.create_text_widget(new_tab))
        self.nb.add(new_tab, text='Untitled.py   ')
        self.nb.select(new_tab)

    def copy(self):
        try:
            sel = self.tabs[self.get_tab()].textbox.get(
                tk.SEL_FIRST, tk.SEL_LAST)
            textbox.clipboard_clear()
            textbox.clipboard_append(sel)
        except:
            pass

    def delete(self):
        try:
            self.tabs[self.get_tab()].textbox.delete(tk.SEL_FIRST, tk.SEL_LAST)
            self.key()
        except:
            pass

    def cut(self):
        try:
            sel = self.tabs[self.get_tab()].textbox.get(
                tk.SEL_FIRST, tk.SEL_LAST)
            textbox.clipboard_clear()
            textbox.clipboard_append(sel)
            self.tabs[self.get_tab()].textbox.delete(tk.SEL_FIRST, tk.SEL_LAST)
            self.key()
        except:
            pass

    def paste(self):
        try:
            self.tabs[self.get_tab()].textbox.insert(tk.INSERT,
                                                     textbox.clipboard_get())
        except:
            pass

    def select_all(self, *args):
        try:
            curr_tab = self.get_tab()
            self.tabs[curr_tab].textbox.tag_add(tk.SEL, '1.0', tk.END)
            self.tabs[curr_tab].textbox.mark_set(tk.INSERT, tk.END)
            self.tabs[curr_tab].textbox.see(tk.INSERT)
        except:
            pass

    def build(self, *args):
        try:
            if _PLTFRM:
                with open('./.temp/build.bat') as f:
                    f.write((_BATCH_BUILD % self.file_dir))
                    os.system('./.temp/build.bat')
            else:
                with open('./.temp/build.sh') as f:
                    f.write((_BATCH_BUILD % self.file_dir))
                    os.system('chmod 700 ./.temp/build.sh && ./.temp/build.sh')
        except:
            pass

    def autoinsert(self, event=None):
        currtext = self.tabs[self.get_tab()].textbox
        # Strings
        if event.char not in ['(', '[', '{']:
            currtext.insert('insert', event.char)
            currtext.mark_set(
                'insert',
                '%d.%s' % (int(float(currtext.index('insert'))),
                           str(int(currtext.index('insert').split('.')[1:][0]) - 1)))
            self.key(event=None)
        # Others
        elif event.char == '(':
            currtext.insert('insert', event.char)
            currtext.insert('insert', ')')
            currtext.mark_set(
                'insert',
                '%d.%s' % (int(float(currtext.index('insert'))),
                           str(int(currtext.index('insert').split('.')[1:][0]) - 1)))
            return 'break'
        elif event.char == '[':
            currtext.insert('insert', event.char)
            currtext.insert('insert', ']')
            currtext.mark_set(
                'insert',
                '%d.%s' % (int(float(currtext.index('insert'))),
                           str(int(currtext.index('insert').split('.')[1:][0]) - 1)))
            return 'break'
        elif event.char == '{':
            currtext.insert('insert', event.char)
            currtext.insert('insert', '}')
            currtext.mark_set(
                'insert',
                '%d.%s' % (int(float(currtext.index('insert'))),
                           str(int(currtext.index('insert').split('.')[1:][0]) - 1)))
            return 'break'

    def autoindent(self, event=None):
        currtext = self.tabs[self.get_tab()].textbox
        indentation = ""
        lineindex = currtext.index("insert").split(".")[0]
        linetext = currtext.get(lineindex + ".0", lineindex + ".end")
        for character in linetext:
            if character in [" ", "\t"]:
                indentation += character
            else:
                break

        if linetext.endswith(":"):
            indentation += " " * 4
        if linetext.endswith("\\"):
            indentation += " " * 4

        currtext.insert(currtext.index("insert"), "\n" + indentation)
        self.key()
        return "break"

    def search(self, event=None):
        searchWin = ttk.Frame(self.tabs[self.get_tab()].textbox.frame)
        style = ThemedStyle(searchWin)
        style.set_theme("black")
        searchWin.pack(side='bottom', fill='x')
        searchWin.focus_set()
        ttk.Label(searchWin, text='Search: ').pack(
            side='left', anchor='nw', fill='y')
        content = tk.Entry(searchWin, background='black',
                           foreground='white', insertbackground='white')
        content.pack(side='left', fill='both')
        content.focus_set()
        butt = ttk.Button(searchWin, text='Highlight Matches')
        butt.pack(side='left')
        butt2 = ttk.Button(searchWin, text='Clear Highlights')
        butt2.pack(side='left')

        def find(event=None):
            text = self.tabs[self.get_tab()].textbox
            text.tag_remove('found', '1.0', 'end')
            s = content.get()
            if s:
                idx = '1.0'
                while 1:
                    idx = text.search(s, idx, nocase=1,
                                      stopindex='end')
                    if not idx:
                        break
                    lastidx = '%s+%dc' % (idx, len(s))
                    text.tag_add('found', idx, lastidx)
                    idx = lastidx
                text.tag_config('found', foreground='red', background='yellow')

        def clear():
            text = self.tabs[self.get_tab()].textbox
            text.tag_remove('found', '1.0', 'end')
        butt.config(command=find)
        butt2.config(command=clear)

        def _exit():
            searchWin.pack_forget()
            clear()
            self.tabs[self.get_tab()].textbox.focus_set()

        ttk.Button(searchWin, text='x', command=_exit,
                   width=1).pack(side='right')

    def undo(self, *args):
        try:
            self.tabs[self.get_tab()].textbox.edit_undo()
        except:
            pass

    def redo(self, *args):
        try:
            self.tabs[self.get_tab()].textbox.edit_redo()
        except:
            pass

    def right_click(self, event):
        self.right_click_menu.post(event.x_root, event.y_root)

    def right_click_tab(self, event):
        self.tab_right_click_menu.post(event.x_root, event.y_root)

    def close_tab(self, event=None):
        try:
            if self.nb.index("end") > 1:
                # Close the current tab if close is selected from file menu, or keyboard shortcut.
                if event is None or event.type == str(2):
                    selected_tab = self.get_tab()
                # Otherwise close the tab based on coordinates of center-click.
                else:
                    try:
                        index = event.widget.index(
                            '@%d,%d' % (event.x, event.y))
                        selected_tab = self.nb._nametowidget(
                            self.nb.tabs()[index])
                    except tk.TclError:
                        return

            self.nb.forget(selected_tab)
            self.tabs.pop(selected_tab)
        except:
            pass

    def exit(self):
        if self.save_changes():
            self.master.destroy()
        else:
            return

    def save_changes(self):
        try:
            curr_tab = self.get_tab()
            file_dir = self.tabs[curr_tab].file_dir

            # Check if any changes have been made, returns False if user chooses to cancel rather than select to save or not.
            if self.tabs[curr_tab].edited:
                # If changes were made since last save, ask if user wants to save.
                m = messagebox.askyesnocancel('Editor', 'Do you want to save changes to ' +
                                              ('Untitled' if not file_dir else file_dir) + '?')

                # If None, cancel.
                if m is None:
                    return False
                # else if True, save.
                elif m is True:
                    self.save_file()
                # else don't save.
                else:
                    pass
        except:
            return True

        return True

    def get_tab(self):
        return self.nb._nametowidget(self.nb.select())

    def move_tab(self, event):
        if self.nb.index('end') > 1:
            y = self.get_tab().winfo_y() - 5

            try:
                self.nb.insert(
                    event.widget.index('@%d,%d' % (event.x, y)), self.nb.select())
            except tk.TclError:
                return

    def version(self):
        ver = tk.Toplevel()
        ver.geometry('480x190')
        ver.resizable(0, 0)
        cv = tk.Canvas(ver)
        cv.pack(fill='both', expand=1)
        img = tk.PhotoImage(file='ver.gif')
        cv.create_image(0, 0, anchor='nw', image=img)
        ver.mainloop()


def main():
    root = ttkthemes.ThemedTk(theme='black')
    app = Editor(root)
    root.mainloop()


if __name__ == '__main__':
    main()

