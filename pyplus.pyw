#!python3
# coding: utf-8
"""
+ =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-= +
| pyplus.pyw -- the editor's ONLY file                |
| The somehow-professional editor                     |
| It's extremely small!!!                             |
| You can visit my site for more details!             |
| vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv            |
| > http://ZCG-coder.github.io/PyPlusWeb <            |
| ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^            |
| You can also contribute it on github!               |
| Note: Some parts are adapted from stack overflow.   |
+ =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-= +
"""
import json
import os
import sys
import tkinter as tk
import tkinter.filedialog
import tkinter.font as tkFont
import tkinter.ttk as ttk
from tkinter import scrolledtext

import pygments
import ttkthemes
from pygments.lexers import PythonLexer
from ttkthemes import ThemedStyle

_PLTFRM = (True if sys.platform.startswith('win') else False)
_OSX = (True if sys.platform.startswith('darwin') else False)
_BATCH_BUILD = ('''
#!/bin/bash

set +v

mytitle="Build Results"

# Require ANSI Escape Code support

python3 ./measure.py start

echo -e '\033k'$mytitle'\033\\'

echo ===================================================

python3 %s

echo Program Finished With Exit Code $?

python3 ./measure.py stop

echo ===================================================

echo Exit in 10 secs...

sleep 10s
''' if not _PLTFRM else '''
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
''')
_MAIN_KEY = 'Command' if _OSX else 'Control'


class EditorErr(Exception):
    """A nice exception class for debugging"""

    def __init__(self, message):
        super().__init__('An editor error is occurred.' if not message else message)


class Settings:
    """A class to read and write data to/from settings.json"""

    def __init__(self):
        with open('settings.json') as f:
            self.settings = json.load(f)
        self.lexer = self.settings['lexer']
        self.font = self.settings['font'].split()[0]
        self.size = self.settings['font'].split()[1]

    def config_lexer(self):
        config = tk.Toplevel()
        config.title("Lexer (Syntax highlighting)")
        tk.Label(config, text='Select the lexer below').pack()
        lexer_cb = ttk.Combobox(config, state="readonly")
        lexer_cb.pack()
        lexers = ['Python3Lexer', 'PythonLexer', 'None (Plain text)']

        lexer_cb['value'] = lexers

        def save():
            self.lexer = lexer_cb.get()
            self.save_settings()
            config.destroy()

        config.protocol("WM_DELETE_WINDOW", save)
        config.mainloop()

    def config_font(self):
        config = tk.Toplevel()
        config.title('Font')
        tk.Label(config, text=f'Enter the font below\nCurrent font is {self.font} {self.size}').pack()
        e = tk.Entry(config)
        e.pack()

        def save():
            font = e.get()
            font = font.split()
            self.font = font[0]
            self.size = font[1]
            self.save_settings()
            config.destroy()

        config.protocol('WM_DELETE_WINDOW', save)
        config.mainloop()

    def save_settings(self):
        self.settings = {"lexer": self.lexer,
                         "font": f'{self.font} {self.size}'}
        with open('settings.json', 'w') as f:
            json.dump(self.settings, f)

    def get_settings(self, setting):
        if setting == 'font':
            return f'{self.font} {self.size}'
        elif setting == 'lexer':
            return self.lexer
        else:
            raise EditorErr


class TextLineNumbers(tk.Canvas):
    def __init__(self, *args, **kwargs):
        tk.Canvas.__init__(self, *args, **kwargs)
        self.textwidget = None

    def attach(self, text_widget):
        self.textwidget = text_widget

    def redraw(self, line):
        """redraw line numbers"""
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
            if str(int(float(i))) == str(line):
                bold_font = tkFont.Font(family=self.textwidget['font'], weight="bold")
                self.create_text(2, y, anchor="nw", text=linenum,
                                 fill='black', font=bold_font)
            else:
                self.create_text(2, y, anchor="nw", text=linenum,
                                 fill='black', font=self.textwidget['font'])
            i = self.textwidget.index("%s+1line" % i)


class CustomText(tk.scrolledtext.ScrolledText):
    def __init__(self, *args, **kwargs):
        tk.scrolledtext.ScrolledText.__init__(self, *args, **kwargs)

        # create a proxy for the underlying widget
        self._orig = self._w + "_orig"
        self.tk.call("rename", self._w, self._orig)
        self.tk.createcommand(self._w, self._proxy)
        self.vbar = ttk.Scrollbar()

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
    """An enhanced text frame to put the
    text widget with linenumbers in."""

    def __init__(self, *args, **kwargs):
        ttk.Frame.__init__(self, *args, **kwargs)
        settings_class = Settings()
        self.font = settings_class.get_settings('font')
        self.text = CustomText(self, bg='black', fg='white', insertbackground='white',
                               selectforeground='black', selectbackground='white', highlightthickness=0,
                               font=self.font, wrap='none')
        self.linenumbers = TextLineNumbers(
            self, width=30, bg='darkgray', bd=0, highlightthickness=0)
        self.linenumbers.attach(self.text)
        self.linenumbers.pack(side="left", fill="y")
        self.text.pack(side="right", fill="both", expand=True)

        self.text.bind("<<Change>>", self._on_change)
        self.text.bind("<Configure>", self._on_change)

    def _on_change(self, event=None):
        currline = int(float(self.text.index('insert linestart')))
        self.linenumbers.redraw(currline)
        self.text.config(font=self.font)


class CustomNotebook(ttk.Notebook):
    """A ttk Notebook with close buttons on each tab
        images drawn by me using the mspaint app (the rubbish in many people's opinion)"""

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
        else:
            self.event_generate("<<Notebook_B1-Down>>", when="tail")

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


class Document():
    """Helper class, for the editor"""

    def __init__(self, Frame, TextWidget, FileDir='', FullDir=''):
        self.file_dir = FileDir
        self.fulldir = FullDir if FullDir else FileDir
        self.textbox = TextWidget


class Editor():
    """The editor class."""

    def __init__(self):
        """The editor object, the entire thing that goes in the
        window.
        Lacks these MacOS support:
        * The file selector cannot change file type.
        """
        settings_class = Settings()
        self.lexer = settings_class.get_settings('lexer')
        if self.lexer == "None (Plain text)":
            print(True)
        self.master = ttkthemes.ThemedTk()
        self.master.minsize(900, 600)
        style = ThemedStyle(self.master)
        style.set_theme("black")  # Apply ttkthemes to master window.
        self.master.geometry("600x400")
        self.master.title('PyEdit +')
        self.master.iconphoto(True, tk.PhotoImage(data='''iVBORw0KGgoAAAANSUhEU
        gAAACAAAAAgBAMAAACBVGfHAAAAAXNSR0IB2cksfwAAAAlwSFlzAAASdAAAEnQB3mYfeAAA
        ABJQTFRFAAAAAAAA////TWyK////////WaqEwgAAAAZ0Uk5TAP8U/yr/h0gXnQAAAHpJREF
        UeJyNktENgCAMROsGog7ACqbpvzs07L+KFCKWFg0XQtLHFQIHAEBoiiAK2BSkXlBpzWDX4D
        QGsRhw9B3SMwNSSj1glNEDqhUpUGw/gMuUd+d2Csny6xgAZB4A1IDwG1SxAc/95t7DAPPIm
        4/BBeWjdGHr73AB3CCCXSvLODzvAAAAAElFTkSuQmCC'''))
        # Base64 image, this probably decreases the repo size.

        self.filetypes = None

        self.tabs = {}

        self.nb = CustomNotebook(self.master, self.close_tab)
        self.nb.bind('<B1-Motion>', self.move_tab)
        self.nb.pack(expand=1, fill='both')
        self.nb.enable_traversal()

        self.master.protocol('WM_DELETE_WINDOW', self.exit)

        menubar = tk.Menu(self.master)

        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label='New Tab', command=self.new_file, accelerator=f'{_MAIN_KEY}-n')
        filemenu.add_command(label='Open File', command=self.open_file, accelerator=f'{_MAIN_KEY}-o')
        filemenu.add_command(label='Save File', command=self.save_file, accelerator=f'{_MAIN_KEY}-s')
        filemenu.add_command(label='Save As...', command=self.save_as, accelerator=f'{_MAIN_KEY}-S')
        filemenu.add_command(label='Close Tab', command=self.close_tab, accelerator=f'{_MAIN_KEY}-w')
        filemenu.add_separator()
        filemenu.add_command(label='Exit Editor', command=self.exit, accelerator=f'{_MAIN_KEY}-q')

        editmenu = tk.Menu(menubar, tearoff=0)
        editmenu.add_command(label='Undo', command=self.undo, accelerator=f'{_MAIN_KEY}-o')
        editmenu.add_command(label='Redo', command=self.redo, accelerator=f'{_MAIN_KEY}-o')
        editmenu.add_separator()
        editmenu.add_command(label='Cut', command=self.cut, accelerator=f'{_MAIN_KEY}-o')
        editmenu.add_command(label='Copy', command=self.copy, accelerator=f'{_MAIN_KEY}-o')
        editmenu.add_command(label='Paste', command=self.paste, accelerator=f'{_MAIN_KEY}-o')
        editmenu.add_command(label='Delete Selected', command=self.delete, accelerator='del')
        editmenu.add_command(label='Select All', command=self.select_all, accelerator=f'{_MAIN_KEY}-a')

        codemenu = tk.Menu(menubar, tearoff=0)
        codemenu.add_command(label='Build', command=self.build, accelerator=f'{_MAIN_KEY}-b')
        codemenu.add_command(label='Search', command=self.search, accelerator=f'{_MAIN_KEY}-f')

        helpmenu = tk.Menu(menubar, tearoff=0)
        helpmenu.add_command(label='Version', command=self.version)

        configmenu = tk.Menu(menubar, tearoff=0)
        configmenu.add_command(label='Configure font', command=self.config_font)
        configmenu.add_command(label='Configure lexer', command=self.config_lexer)

        menubar.add_cascade(label='File', menu=filemenu)
        menubar.add_cascade(label='Edit', menu=editmenu)
        menubar.add_cascade(label='Code', menu=codemenu)
        menubar.add_cascade(label='Settings', menu=configmenu)
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
        self.nb.bind(('<Button-2>' if _OSX else '<Button-3>'), self.right_click_tab)
        # Mouse bindings
        first_tab = ttk.Frame(self.nb)
        self.tabs[first_tab] = Document(
            first_tab, self.create_text_widget(first_tab))
        self.nb.add(first_tab, text='Untitled.py   ')
        self.mouse()

        def tab(event):
            self.tabs[self.get_tab()].textbox.insert('insert', ' ' * 4)  # Convert tabs to spaces
            return 'break'  # Quit quickly, before a char is being inserted.

        # Keyboard bindings
        self.master.bind(f'<{_MAIN_KEY}-s>', self.save_file)
        self.master.bind(f'<{_MAIN_KEY}-w>', self.close_tab)
        self.master.bind(('<Button-2>' if _OSX else '<Button-3>'), self.right_click)
        self.master.bind(f'<{_MAIN_KEY}-z>', self.undo)
        self.master.bind(f'<{_MAIN_KEY}-Z>', self.redo)
        self.master.bind(f'<{_MAIN_KEY}-b>', self.build)
        self.master.bind(f'<{_MAIN_KEY}-f>', self.search)
        self.master.bind(f'<{_MAIN_KEY}-n>', self.new_file)
        self.master.bind('<Tab>', tab)
        for x in ['"', "'", '(', '[', '{']:
            self.master.bind(x, self.autoinsert)
        self.open_file('pyplus.pyw')
        self.master.mainloop()  # This line can be here only

    def create_text_widget(self, frame):
        """Creates a text widget in a frame."""
        textframe = EnhancedTextFrame(frame)  # The one with line numbers and a nice dark theme
        textframe.pack(fill='both', expand=1)

        textbox = textframe.text  # text widget
        textbox.frame = frame  # The text will be packed into the frame.
        # TODO: Make a better color scheme
        textbox.tag_configure("Token.Keyword", foreground="#CC7A00")
        textbox.tag_configure("Token.Keyword.Constant", foreground="#CC7A00")
        textbox.tag_configure("Token.Keyword.Declaration", foreground="#CC7A00")
        textbox.tag_configure("Token.Keyword.Namespace", foreground="#CC7A00")
        textbox.tag_configure("Token.Keyword.Pseudo", foreground="#CC7A00")
        textbox.tag_configure("Token.Keyword.Reserved", foreground="#CC7A00")
        textbox.tag_configure("Token.Keyword.Type", foreground="#CC7A00")
        textbox.tag_configure("Token.Name.Class", foreground="#ddd313")
        textbox.tag_configure("Token.Name.Exception", foreground="#ddd313")
        textbox.tag_configure("Token.Name.Function", foreground="#298fb5")
        textbox.tag_configure("Token.Name.Function.Magic", foreground="#298fb5")
        textbox.tag_configure("Token.Name.Decorator", foreground="#298fb5")
        textbox.tag_configure("Token.Name.Builtin", foreground="#CC7A00")
        textbox.tag_configure("Token.Name.Builtin.Pseudo", foreground="#CC7A00")
        textbox.tag_configure("Token.Comment", foreground="#767d87")
        textbox.tag_configure("Token.Comment.Single", foreground="#767d87")
        textbox.tag_configure("Token.Comment.Double", foreground="#767d87")
        textbox.tag_configure("Token.Literal.Number.Integer", foreground="#88daea")
        textbox.tag_configure("Token.Literal.Number.Float", foreground="#88daea")
        textbox.tag_configure("Token.Literal.String.Single", foreground="#35c666")
        textbox.tag_configure("Token.Literal.String.Double", foreground="#35c666")
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
        # ^ Highlight using tags
        textbox.bind('<Return>', self.autoindent)
        textbox.bind("<<KeyEvent>>", self.key)
        textbox.bind("<<MouseEvent>>", self.mouse)
        textbox.event_add("<<KeyEvent>>", "<KeyRelease>")
        textbox.event_add("<<MouseEvent>>", "<ButtonRelease>")
        textbox.statusbar = ttk.Label(
            frame, text='PyEdit +', justify='right', anchor='e')
        textbox.statusbar.pack(side='bottom', fill='x', anchor='e')

        self.master.geometry('1000x600')  # Configure window size
        textbox.focus_set()
        return textbox

    def key(self, _=None):
        """Event when a key is pressed."""
        currtext = self.tabs[self.get_tab()].textbox
        try:
            self._highlight_all()
            currtext.statusbar.config(
                text=f'PyEdit+ | file {self.nb.tab(self.get_tab())["text"]}| ln {int(float(currtext.index("insert")))} | col {str(int(currtext.index("insert").split(".")[1:][0]))}')
            # Update statusbar
            # Auto-save
            self.save_file()
        except Exception as e:
            currtext.statusbar.config(text=f'PyEdit + {e}')  # When error occurs

    def mouse(self, _=None):
        """The action done when the mouse is clicked"""
        currtext = self.tabs[self.get_tab()].textbox
        try:
            currtext.statusbar.config(
                text=f"PyEdit+ | file {self.nb.tab(self.get_tab())['text']}| ln {int(float(currtext.index('insert')))} | col {str(int(currtext.index('insert').split('.')[1:][0]))}")
            # Update statusbar and titlebar
        except Exception as e:
            currtext.statusbar.config(text=f'PyEdit + {str(e)}')  # When error occurs

    def _highlight_all(self):
        """Highlight the text in the text box."""
        currtext = self.tabs[self.get_tab()].textbox

        start_index = currtext.index('1.0')
        end_index = currtext.index(tk.END)
        tri_str_start = []
        tri_str_end = []
        cursor_pos = float(currtext.index('insert-1c linestart')) * 10
        for index, linenum in enumerate(currtext.tag_ranges('Token.Literal.String.Doc')):
            if index % 2 == 1:
                tri_str_end.append(int(float(str(linenum)) * 10))
            else:
                tri_str_start.append(int(float(str(linenum)) * 10))

        for x in tri_str_start:
            pass

        for tag in currtext.tag_names():
            if tag == 'sel':
                continue
            currtext.tag_remove(
                tag, start_index, end_index)

        code = currtext.get(start_index, end_index)

        for index, line in enumerate(code):
            if index == 0 and line != '\n':
                break
            elif line == '\n':
                start_index = currtext.index(f'{start_index}+1line')
            else:
                break

        currtext.mark_set('range_start', start_index)
        for token, content in pygments.lex(code, PythonLexer()):
            currtext.mark_set('range_end', f'range_start + {len(content)}c')
            currtext.tag_add(
                str(token), 'range_start', 'range_end')
            currtext.mark_set(
                'range_start', 'range_end')
        currtext.tag_configure('hi', foreground='white')
        self.master.update()
        self.master.update_idletasks()

    def open_file(self, file=''):
        """Opens a file
        If a file is not provided, a messagebox'll
        pop up to ask the user to select the path.
        """
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
                # Inserts file content, replacing tabs with four spaces
                self.tabs[new_tab].textbox.focus_set()
                self.mouse()
                self._highlight_all()
            except:
                return

    def save_as(self):
        """Saves a *new* file"""
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
        """Saves an *existing* file"""
        try:
            curr_tab = self.get_tab()
            if not self.tabs[curr_tab].file_dir:
                self.save_as()
            else:
                with open(self.tabs[curr_tab].file_dir, 'w') as file:
                    file.write(self.tabs[curr_tab].textbox.get(1.0, 'end').strip())
        except:
            pass

    def new_file(self, *args):
        """Creates a new tab(file)."""
        new_tab = ttk.Frame(self.nb)
        self.tabs[new_tab] = Document(
            new_tab, self.create_text_widget(new_tab))
        self.nb.add(new_tab, text='Untitled.py   ')
        self.nb.select(new_tab)

    def copy(self):
        try:
            sel = self.tabs[self.get_tab()].textbox.get(
                tk.SEL_FIRST, tk.SEL_LAST)
            self.tabs[self.get_tab()].textbox.clipboard_clear()
            self.tabs[self.get_tab()].textbox.clipboard_append(sel)
        except:
            pass

    def delete(self):
        try:
            self.tabs[self.get_tab()].textbox.delete(tk.SEL_FIRST, tk.SEL_LAST)
            self.key()
        except:
            pass

    def cut(self, textbox=None):
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
                                                     self.tabs[self.get_tab()].textbox.clipboard_get())
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
        """Builds the file
        Steps:
        1) Writes build code into the batch file.
        2) Linux only: uses chmod to make the sh execuable
        3) Runs the build file"""
        try:
            if _PLTFRM:  # Windows
                with open('build.bat') as f:
                    f.write((_BATCH_BUILD % self.tabs[self.get_tab()].file_dir))
                    os.system('build.bat')
            else:
                with open('build.sh') as f:
                    f.write((_BATCH_BUILD % self.tabs[self.get_tab()].file_dir))
                    os.system('chmod 700 build.sh && build.sh')
        except:
            pass

    def autoinsert(self, event=None):
        """Auto-inserts a symbol
        * ' -> ''
        * " -> ""
        * ( -> ()
        * [ -> []
        * { -> {}"""
        currtext = self.tabs[self.get_tab()].textbox
        # Strings
        if event.char not in ['(', '[', '{']:
            currtext.insert('insert', event.char)
            currtext.mark_set(
                'insert',
                '%d.%s' % (int(float(currtext.index('insert'))),
                           str(int(currtext.index('insert').split('.')[1:][0]) - 1)))
            self.key()
        # Others
        elif event.char == '(':
            currtext.insert('insert', ')')
            currtext.mark_set(
                'insert',
                '%d.%s' % (int(float(currtext.index('insert'))),
                           str(int(currtext.index('insert').split('.')[1:][0]) - 1)))
            return 'break'
        elif event.char == '[':
            currtext.insert('insert', ']')
            currtext.mark_set(
                'insert',
                '%d.%s' % (int(float(currtext.index('insert'))),
                           str(int(currtext.index('insert').split('.')[1:][0]) - 1)))
            return 'break'
        elif event.char == '{':
            currtext.insert('insert', '}')
            currtext.mark_set(
                'insert',
                '%d.%s' % (int(float(currtext.index('insert'))),
                           str(int(currtext.index('insert').split('.')[1:][0]) - 1)))
            return 'break'

    def autoindent(self, event=None):
        """Auto-indents the next line"""
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

    def search(self):
        """Searches through the file"""
        searchenabled = False
        searchWin = ttk.Frame(self.tabs[self.get_tab()].textbox.frame)
        style = ThemedStyle(searchWin)
        style.set_theme("black")
        try:
            if searchenabled:
                searchWin.pack(side='bottom', fill='x')
        except:
            pass

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
            if self.nb.index("end"):
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
            if len(self.tabs) == 0:
                self.open_file('HI.txt')
        except:
            pass

    def exit(self):
        sys.exit(0)

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
        """Shows the version and related info of the editor."""
        ver = tk.Toplevel()
        style = ThemedStyle(ver)
        style.set_theme('black')  # Applies the ttk theme
        ver.geometry('480x190')
        ver.resizable(0, 0)
        cv = tk.Canvas(ver)
        cv.pack(fill='both', expand=1)
        img = tk.PhotoImage(file='ver.gif')
        cv.create_image(0, 0, anchor='nw', image=img)
        ver.mainloop()

    def config_font(self, event=None):
        config = Settings()
        config.config_font()

    def config_lexer(self, event=None):
        config = Settings()
        config.config_lexer()
        self._highlight_all()


if __name__ == '__main__':
    Editor()  # Execs the main class