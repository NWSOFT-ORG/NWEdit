#!python3
# coding: utf-8
"""
+ =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-= +
| pyplus.py -- the editor's ONLY file                |
| The somehow-professional editor                     |
| It's extremely small! (around 40 kB)                |
| You can visit my site for more details!             |
| vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv            |
| > http://ZCG-coder.github.io/PyPlusWeb <            |
| ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^            |
| You can also contribute it on github!               |
| Note: Some parts are adapted from stack overflow.   |
+ =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-= +
Also, it's cross-compatable!
"""
import json
import os
import os.path
import platform
import shlex
import subprocess
import sys
import tkinter as tk
import tkinter.filedialog
import tkinter.font as tkFont
import tkinter.ttk as ttk
from tkinter import scrolledtext

import pygments
import ttkthemes
from pygments.lexers.html import XmlLexer
from pygments.lexers.python import PythonLexer
from pygments.lexers.special import TextLexer
from ttkthemes import ThemedStyle

_PLTFRM = (True if sys.platform.startswith('win') else False)
_OSX = (True if sys.platform.startswith('darwin') else False)
_BATCH_BUILD = ('''#!/bin/bash
set +v
python3 ./measure.py start
python3 -c 'print("==================== OUTPUT ====================")'
python3 {}
python3 -c 'print("================================================")'
echo Program Finished With Exit Code $?
python3 ./measure.py stop
echo Press enter to continue...
read -s  # This will pause the script
''' if not _PLTFRM else '''@echo off
title Build Results
measure.py start
echo.
echo.
echo ----------------------------------------------------
python3 {}
echo Program Finished With Exit Code %ERRORLEVEL%
measure.py stop
echo ----------------------------------------------------
echo.
pause
''')  # The batch files for building.
_MAIN_KEY = 'Command' if _OSX else 'Control'  # MacOS uses Cmd, but others uses Ctrl
_TK_VERSION = int(float(tk.TkVersion) * 10)  # Gets tk's version


# From thonny
def update_system_path(env, value):
    # in Windows, env keys are not case sensitive
    # this is important if env is a dict (not os.environ)
    if platform.system() == "Windows":
        found = False
        for key in env:
            if key.upper() == "PATH":
                found = True
                env[key] = value

        if not found:
            env["PATH"] = value
    else:
        env["PATH"] = value


def get_environment_with_overrides(overrides):
    env = os.environ.copy()
    for key in overrides:
        if overrides[key] is None and key in env:
            del env[key]
        else:
            assert isinstance(overrides[key], str)
            if key.upper() == "PATH":
                update_system_path(env, overrides[key])
            else:
                env[key] = overrides[key]
    return env


def run_in_terminal(cmd, cwd=os.getcwd(), env_overrides={}, keep_open=True, title=None):
    env = get_environment_with_overrides(env_overrides)

    if not cwd or not os.path.exists(cwd):
        cwd = os.getcwd()

    if platform.system() == "Windows":
        _run_in_terminal_in_windows(cmd, cwd, env, keep_open, title)
    elif platform.system() == "Linux":
        _run_in_terminal_in_linux(cmd, cwd, env, keep_open)
    elif platform.system() == "Darwin":
        _run_in_terminal_in_macos(cmd, cwd, env_overrides, keep_open)
    else:
        raise RuntimeError("Can't launch terminal in " + platform.system())


def open_system_shell(cwd, env_overrides={}):
    env = get_environment_with_overrides(env_overrides)

    if platform.system() == "Darwin":
        _run_in_terminal_in_macos([], cwd, env_overrides, True)
    elif platform.system() == "Windows":
        cmd = "start cmd"
        subprocess.Popen(cmd, cwd=cwd, env=env, shell=True)
    elif platform.system() == "Linux":
        cmd = _get_linux_terminal_command()
        subprocess.Popen(cmd, cwd=cwd, env=env, shell=True)
    else:
        raise RuntimeError("Can't launch terminal in " + platform.system())


def _add_to_path(directory, path):
    # Always prepending to path may seem better, but this could mess up other things.
    # If the directory contains only one Python distribution executables, then
    # it probably won't be in path yet and therefore will be prepended.
    if (
            directory in path.split(os.pathsep)
            or platform.system() == "Windows"
            and directory.lower() in path.lower().split(os.pathsep)
    ):
        return path
    else:
        return directory + os.pathsep + path


def _run_in_terminal_in_windows(cmd, cwd, env, keep_open, title=None):
    if keep_open:
        # Yes, the /K argument has weird quoting. Can't explain this, but it works
        quoted_args = " ".join(
            map(lambda s: s if s == "&" else '"' + s + '"', cmd))
        cmd_line = """start {title} /D "{cwd}" /W cmd /K "{quoted_args}" """.format(
            cwd=cwd, quoted_args=quoted_args, title='"' + title + '"' if title else ""
        )

        subprocess.Popen(cmd_line, cwd=cwd, env=env, shell=True)
    else:
        subprocess.Popen(
            cmd, creationflags=subprocess.CREATE_NEW_CONSOLE, cwd=cwd, env=env)


def _run_in_terminal_in_linux(cmd, cwd, env, keep_open):
    def _shellquote(s):
        return subprocess.list2cmdline([s])

    term_cmd = _get_linux_terminal_command()

    if isinstance(cmd, list):
        cmd = " ".join(map(_shellquote, cmd))

    if keep_open:
        # http://stackoverflow.com/a/4466566/261181
        core_cmd = "{cmd}; exec bash -i".format(cmd=cmd)
        in_term_cmd = "bash -c {core_cmd}".format(
            core_cmd=_shellquote(core_cmd))
    else:
        in_term_cmd = cmd

    if term_cmd == "lxterminal":
        # https://www.raspberrypi.org/forums/viewtopic.php?t=221490
        whole_cmd = "{term_cmd} --command={in_term_cmd}".format(
            term_cmd=term_cmd, in_term_cmd=_shellquote(in_term_cmd)
        )
    else:
        whole_cmd = "{term_cmd} -e {in_term_cmd}".format(
            term_cmd=term_cmd, in_term_cmd=_shellquote(in_term_cmd)
        )

    if term_cmd == "terminator" and "PYTHONPATH" in env:
        # it is written in Python 2 and the PYTHONPATH of Python 3 will confuse it
        # https://github.com/thonny/thonny/issues/1129
        del env["PYTHONPATH"]

    subprocess.Popen(whole_cmd, cwd=cwd, env=env, shell=True)


def _run_in_terminal_in_macos(cmd, cwd, env_overrides, keep_open):
    _shellquote = shlex.quote

    cmds = "clear; cd " + _shellquote(cwd)
    # osascript "tell application" won't change Terminal's env
    # (at least when Terminal is already active)
    # At the moment I just explicitly set some important variables
    for key in env_overrides:
        if env_overrides[key] is None:
            cmds += "; unset " + key
        else:
            value = env_overrides[key]
            if key == "PATH":
                value = _normalize_path(value)

            cmds += "; export {key}={value}".format(
                key=key, value=_shellquote(value))

    if cmd:
        if isinstance(cmd, list):
            cmd = " ".join(map(_shellquote, cmd))
        cmds += "; " + cmd

    if not keep_open:
        cmds += "; exit"

    # try to shorten to avoid too long line https://github.com/thonny/thonny/issues/1529

    common_prefix = os.path.normpath(sys.prefix).rstrip("/")
    cmds = (
        "export THOPR=" + common_prefix + " ; " +
        cmds.replace(common_prefix + "/", "$THOPR" + "/")
    )
    print(cmds)

    # The script will be sent to Terminal with 'do script' command, which takes a string.
    # We'll prepare an AppleScript string literal for this
    # (http://stackoverflow.com/questions/10667800/using-quotes-in-a-applescript-string):
    cmd_as_apple_script_string_literal = (
        '"' + cmds.replace("\\", "\\\\").replace('"',
                                                 '\\"').replace("$", "\\$") + '"'
    )

    # When Terminal is not open, then do script opens two windows.
    # do script ... in window 1 would solve this, but if Terminal is already
    # open, this could run the script in existing terminal (in undesirable env on situation)
    # That's why I need to prepare two variations of the 'do script' command
    doScriptCmd1 = """        do script %s """ % cmd_as_apple_script_string_literal
    doScriptCmd2 = """        do script %s in window 1 """ % cmd_as_apple_script_string_literal

    # The whole AppleScript will be executed with osascript by giving script
    # lines as arguments. The lines containing our script need to be shell-quoted:
    quotedCmd1 = subprocess.list2cmdline([doScriptCmd1])
    quotedCmd2 = subprocess.list2cmdline([doScriptCmd2])

    # Now we can finally assemble the osascript command line
    cmd_line = (
        "osascript"
        + """ -e 'if application "Terminal" is running then ' """
        + """ -e '    tell application "Terminal"' """
        + """ -e """
        + quotedCmd1
        + """ -e '        activate' """
        + """ -e '    end tell' """
        + """ -e 'else' """
        + """ -e '    tell application "Terminal"' """
        + """ -e """
        + quotedCmd2
        + """ -e '        activate' """
        + """ -e '    end tell' """
        + """ -e 'end if' """
    )

    subprocess.Popen(cmd_line, cwd=cwd, shell=True)


def _get_linux_terminal_command():
    import shutil

    xte = shutil.which("x-terminal-emulator")
    if xte:
        if os.path.realpath(xte).endswith("/lxterminal") and shutil.which("lxterminal"):
            # need to know exact program, because it needs special treatment
            return "lxterminal"
        elif os.path.realpath(xte).endswith("/terminator") and shutil.which("terminator"):
            # https://github.com/thonny/thonny/issues/1129
            return "terminator"
        else:
            return "x-terminal-emulator"
    # Older konsole didn't pass on the environment
    elif shutil.which("konsole"):
        if (
                shutil.which("gnome-terminal")
                and "gnome" in os.environ.get("DESKTOP_SESSION", "").lower()
        ):
            return "gnome-terminal"
        else:
            return "konsole"
    elif shutil.which("gnome-terminal"):
        return "gnome-terminal"
    elif shutil.which("xfce4-terminal"):
        return "xfce4-terminal"
    elif shutil.which("lxterminal"):
        return "lxterminal"
    elif shutil.which("xterm"):
        return "xterm"
    else:
        raise RuntimeError("Don't know how to open terminal emulator")


def _normalize_path(s):
    parts = s.split(os.pathsep)
    return os.pathsep.join([os.path.normpath(part) for part in parts])


# End


class EditorErr(Exception):
    """A nice exception class for debugging"""

    def __init__(self, message):
        # The error (e+m)
        super().__init__('An editor error is occurred.' if not message else message)


class Settings:
    """A class to read data to/from settings.json"""

    def __init__(self):
        with open('settings.json') as f:
            self.settings = json.load(f)
        self.lexer = self.settings['lexer']
        self.font = self.settings['font'].split()[0]
        self.size = self.settings['font'].split()[1]
        self.filetype = self.settings['file_types']

    def get_settings(self, setting):
        if setting == 'font':
            return f'{self.font} {self.size}'
        elif setting == 'lexer':
            if self.lexer == 'txt':
                return TextLexer
            elif self.lexer == 'py':
                return PythonLexer
            elif self.lexer == 'xml':
                return XmlLexer
            else:
                raise EditorErr('The lexer is invalid.')
        elif setting == 'file_type':
            # Always starts with ('All files', '*.*')
            if self.filetype == 'all':
                return (('All files', '*.*'),)
            elif self.filetype == 'py':
                # Extend this list, since Python has a lot of file tyeps
                return ('All files', '*.*'), ('Python Files', '*.py *.pyw *.pyx *.py3 *.pyi'),
            elif self.filetype == 'txt':
                return ('All files', '*.*'), ('Text documents', '*.txt *.rst'),
            elif self.filetype == 'xml':
                # Extend this, since xml has a lot of usage formats
                return ('All files', '*.*'), ('XML', '*.xml *.plist *.iml *.rss'),
            else:
                raise EditorErr(
                    'The file type is not supported by this editor (yet)')
        else:
            raise EditorErr('The setting is not defined')


class TextLineNumbers(tk.Canvas):
    """Line numbers class for tkinter text widgets. From stackoverflow."""

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
                bold_font = tkFont.Font(
                    family=Settings().get_settings('font'), weight="bold")
                self.create_text(2, y, anchor="nw", text=linenum,
                                 fill='black', font=bold_font)
            else:
                self.create_text(2, y, anchor="nw", text=linenum,
                                 fill='black', font=self.textwidget['font'])
            i = self.textwidget.index("%s+1line" % i)


class EnhancedText(tk.scrolledtext.ScrolledText):
    """Text widget, but 'records' your key actions
    If you hit a key, or the text widget's content has changed,
    it generats an event, to redraw the line numbers."""

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
        self.text = EnhancedText(self, bg='black', fg='white', insertbackground='white',
                                 selectforeground='black', selectbackground='white', highlightthickness=0,
                                 font=self.font, wrap='none')
        self.linenumbers = TextLineNumbers(
            self, width=30, bg='darkgray', bd=0, highlightthickness=0)
        self.linenumbers.attach(self.text)
        self.linenumbers.pack(side="left", fill="y")
        self.text.pack(side="right", fill="both", expand=True)

        self.text.bind("<<Change>>", self._on_change)
        self.text.bind("<Configure>", self._on_change)

    def _on_change(self, _=None):
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
        )  # The images, 32x32-sized

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
        # Change the layout, makes it look like this:
        # +------------+
        # | title   [X]|
        # +-------------------------


class Document:
    """Helper class, for the editor"""

    def __init__(self, Frame, TextWidget, FileDir):
        self.file_dir = FileDir
        self.textbox = TextWidget


class Editor:
    """The editor class."""

    def __init__(self):
        """The editor object, the entire thing that goes in the
        window.
        Lacks these MacOS support:
        * The file selector does not work.
        """
        self.settings_class = Settings()
        self.lexer = self.settings_class.get_settings('lexer')
        self.master = ttkthemes.ThemedTk()
        self.master.minsize(900, 600)
        style = ThemedStyle(self.master)
        style.set_theme("black")  # Apply ttkthemes to master window.
        self.master.geometry("600x400")
        self.master.title('PyEdit +')
        self.master.iconphoto(True, tk.PhotoImage(data=('iVBORw0KGgoAAAANSUhEU\n'
                                                        '        gAAACAAAAAgBAMAAACBVGfHAAAAAXNSR0IB2cksfwAAAAlwSFlzAAASdAAAEnQB3mYfeAAA\n'
                                                        '        ABJQTFRFAAAAAAAA////TWyK////////WaqEwgAAAAZ0Uk5TAP8U/yr/h0gXnQAAAHpJREF\n'
                                                        'UeJyNktENgCAMROsGog7ACqbpvzs07L'
                                                        '+KFCKWFg0XQtLHFQIHAEBoiiAK2BSkXlBpzWDX4D\n '
                                                        'QGsRhw9B3SMwNSSj1glNEDqhUpUGw/gMuUd+d2Csny6xgAZB4A1IDwG1SxAc'
                                                        '/95t7DAPPIm\n '
                                                        '        4/BBeWjdGHr73AB3CCCXSvLODzvAAAAAElFTkSuQmCC')))
        # Base64 image, this probably decreases the repo size.

        self.filetypes = self.settings_class.get_settings('file_type')

        self.tabs = {}

        self.nb = CustomNotebook(self.master, self.close_tab)
        self.nb.bind('<B1-Motion>', self.move_tab)
        self.nb.pack(expand=1, fill='both')
        self.nb.enable_traversal()

        self.master.protocol('WM_DELETE_WINDOW',
                             self.exit)  # When the window is closed, or quit from Mac, do exit action

        menubar = tk.Menu(self.master)
        # Name can be apple only, don't really know why!
        app_menu = tk.Menu(menubar, name='apple', tearoff=0)

        app_menu.add_command(label='About PyEdit +', command=self.version)

        if _TK_VERSION < 85 or not _OSX:
            app_menu.add_command(label="Preferences...", command=self.config)
        else:
            self.master.createcommand(
                'tk::mac::ShowPreferences', self.config)  # OS X

        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(
            label='New Tab', command=self.new_file, accelerator=f'{_MAIN_KEY}-n')
        filemenu.add_command(
            label='Open File', command=self.open_file, accelerator=f'{_MAIN_KEY}-o')
        filemenu.add_command(
            label='Close Tab', command=self.close_tab, accelerator=f'{_MAIN_KEY}-w')
        filemenu.add_separator()
        filemenu.add_command(label='Exit Editor',
                             command=self.exit, accelerator=f'{_MAIN_KEY}-q')

        editmenu = tk.Menu(menubar, tearoff=0)
        editmenu.add_command(label='Undo', command=self.undo,
                             accelerator=f'{_MAIN_KEY}-z')
        editmenu.add_command(label='Redo', command=self.redo,
                             accelerator=f'{_MAIN_KEY}-Shift-z')
        editmenu.add_separator()
        editmenu.add_command(label='Cut', command=self.cut,
                             accelerator=f'{_MAIN_KEY}-x')
        editmenu.add_command(label='Copy', command=self.copy,
                             accelerator=f'{_MAIN_KEY}-c')
        editmenu.add_command(label='Paste', command=self.paste,
                             accelerator=f'{_MAIN_KEY}-v')
        editmenu.add_command(label='Delete Selected', command=self.delete)
        editmenu.add_command(
            label='Select All', command=self.select_all, accelerator=f'{_MAIN_KEY}-a')

        self.codemenu = tk.Menu(menubar, tearoff=0)
        self.codemenu.add_command(
            label='Build', command=self.build, accelerator=f'{_MAIN_KEY}-b')
        self.codemenu.add_command(label='Lint', command=self.lint_source)
        self.codemenu.add_command(
            label='Search', command=self.search, accelerator=f'{_MAIN_KEY}-f')

        navmenu = tk.Menu(menubar, tearoff=0)
        navmenu.add_command(label='Go to ...', command=self.goto,
                            accelerator=f'{_MAIN_KEY}-Shift-N')

        menubar.add_cascade(label='App', menu=app_menu)  # App menu
        menubar.add_cascade(label='File', menu=filemenu)
        menubar.add_cascade(label='Edit', menu=editmenu)
        menubar.add_cascade(label='Code', menu=self.codemenu)
        menubar.add_cascade(label='Navigate', menu=navmenu)
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
        self.nb.bind(('<Button-2>' if _OSX else '<Button-3>'),
                     self.right_click_tab)
        # Mouse bindings
        first_tab = ttk.Frame(self.nb)
        self.tabs[first_tab] = Document(
            first_tab, self.create_text_widget(first_tab), FileDir='None')
        self.nb.add(first_tab, text='Untitled.py   ')
        self.mouse()
        self.master.after(0, self.update_settings)

        def tab(_=None):
            self.tabs[self.get_tab()].textbox.insert(
                'insert', ' ' * 4)  # Convert tabs to spaces
            return 'break'  # Quit quickly, before a char is being inserted.

        # Keyboard bindings
        self.master.bind(f'<{_MAIN_KEY}-w>', self.close_tab)
        self.master.bind(f'<{_MAIN_KEY}-z>', self.undo)
        self.master.bind(f'<{_MAIN_KEY}-Z>', self.redo)
        self.master.bind(f'<{_MAIN_KEY}-b>', self.build)
        self.master.bind(f'<{_MAIN_KEY}-f>', self.search)
        self.master.bind(f'<{_MAIN_KEY}-n>', self.new_file)
        self.master.bind(f'<{_MAIN_KEY}-N>', self.goto)
        self.master.bind(f'<BackSpace>', self._del)
        self.master.bind('<Tab>', tab)
        for x in ['"', "'", '(', '[', '{']:
            self.master.bind(x, self.autoinsert)
        self.master.mainloop()  # This line can be here only

    def create_text_widget(self, frame):
        """Creates a text widget in a frame."""
        textframe = EnhancedTextFrame(
            frame)  # The one with line numbers and a nice dark theme
        textframe.pack(fill='both', expand=1)

        textbox = textframe.text  # text widget
        textbox.frame = frame  # The text will be packed into the frame.
        # TODO: Make a better color scheme
        textbox.tag_configure("Token.Keyword", foreground="#61EBFF")
        textbox.tag_configure("Token.Keyword.Constant", foreground="#CC7A00")
        textbox.tag_configure("Token.Keyword.Declaration",
                              foreground="#CC7A00")
        textbox.tag_configure("Token.Keyword.Namespace", foreground="#CC7A00")
        textbox.tag_configure("Token.Keyword.Pseudo", foreground="#CC7A00")
        textbox.tag_configure("Token.Keyword.Reserved", foreground="#CC7A00")
        textbox.tag_configure("Token.Keyword.Type", foreground="#CC7A00")
        textbox.tag_configure('Token.Comment.Hashbang', foreground='#73d216')

        textbox.tag_configure("Token.Name.Class", foreground="#ddd313")
        textbox.tag_configure("Token.Name.Exception", foreground="#ddd313")
        textbox.tag_configure("Token.Name.Function", foreground="#298fb5")
        textbox.tag_configure("Token.Name.Function.Magic",
                              foreground="#298fb5")
        textbox.tag_configure("Token.Name.Decorator", foreground="#298fb5")
        textbox.tag_configure("Token.Name.Builtin", foreground="#CC7A00")
        textbox.tag_configure("Token.Name.Builtin.Pseudo",
                              foreground="#CC7A00")

        textbox.tag_configure("Token.Comment", foreground="#767d87")
        textbox.tag_configure("Token.Comment.Single", foreground="#767d87")
        textbox.tag_configure("Token.Comment.Double", foreground="#767d87")
        textbox.tag_configure("Token.Comment.Shebang", foreground="#00ff00")

        textbox.tag_configure(
            "Token.Literal.Number.Integer", foreground="#88daea")
        textbox.tag_configure(
            "Token.Literal.Number.Float", foreground="#88daea")

        textbox.tag_configure(
            "Token.Literal.String.Single", foreground="#35c666")
        textbox.tag_configure(
            "Token.Literal.String.Double", foreground="#35c666")
        textbox.tag_configure('Token.Literal.String.Doc', foreground='#ff0000')
        # ^ Highlight using tags
        textbox.bind('<Return>', self.autoindent)
        textbox.bind("<<KeyEvent>>", self.key)
        textbox.bind("<<MouseEvent>>", self.mouse)
        textbox.event_add("<<KeyEvent>>", "<KeyRelease>")
        textbox.event_add("<<MouseEvent>>", "<ButtonRelease>")
        textbox.statusbar = ttk.Label(
            frame, text='PyEdit +', justify='right', anchor='e')
        textbox.statusbar.pack(side='bottom', fill='x', anchor='e')
        textbox.bind(('<Button-2>' if _OSX else '<Button-3>'),
                     self.right_click)

        self.master.geometry('1000x600')  # Configure window size
        textbox.focus_set()
        return textbox

    def settitle(self, _=None):
        self.master.title(f'PyEdit + -- {self.tabs[self.get_tab()].file_dir}')

    def key(self, _=None):
        """Event when a key is pressed."""
        currtext = self.tabs[self.get_tab()].textbox
        try:
            self._highlight_line()
            currtext.statusbar.config(
                text=f'PyEdit+ | file {self.nb.tab(self.get_tab())["text"]}| ln {int(float(currtext.index("insert")))} | col {str(int(currtext.index("insert").split(".")[1:][0]))}')
            # Update statusbar and titlebar
            self.settitle()
            # Auto-save
            self.save_file()
        except Exception as e:
            print(str(e))
            currtext.statusbar.config(text=f'PyEdit +')  # When error occurs

    def mouse(self, _=None):
        """The action done when the mouse is clicked"""
        currtext = self.tabs[self.get_tab()].textbox
        try:
            currtext.statusbar.config(
                text=f"PyEdit+ | file {self.nb.tab(self.get_tab())['text']}| ln {int(float(currtext.index('insert')))} | col {str(int(currtext.index('insert').split('.')[1:][0]))}")
            # Update statusbar and titlebar
            self.settitle()
        except Exception:
            currtext.statusbar.config(text=f'PyEdit +')  # When error occurs

    def _highlight_all(self):
        """Highlight the text in the text box."""
        currtext = self.tabs[self.get_tab()].textbox

        start_index = currtext.index('1.0')
        end_index = currtext.index(tk.END)

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
        for token, content in pygments.lex(code, self.lexer()):
            currtext.mark_set('range_end', f'range_start + {len(content)}c')
            currtext.tag_add(
                str(token), 'range_start', 'range_end')
            currtext.mark_set(
                'range_start', 'range_end')
        currtext.tag_configure('hi', foreground='white')
        self.master.update()
        self.master.update_idletasks()

    def _highlight_line(self):
        """Highlight the text in the text box."""
        currtext = self.tabs[self.get_tab()].textbox

        start_index = currtext.index('insert-1c linestart')
        end_index = currtext.index('insert-1c lineend')

        tri_str_start = []
        tri_str_end = []
        tri_str = []
        cursor_pos = float(currtext.index('insert'))
        for index, linenum in enumerate(
                currtext.tag_ranges('Token.Literal.String.Doc') + currtext.tag_ranges('Token.Literal.String.Single')):
            if index % 2 == 1:
                tri_str_end.append(float(str(linenum)))
            else:
                tri_str_start.append(float(str(linenum)))

        for index, value in enumerate(tri_str_start):
            tri_str.append((value, tri_str_end[index]))

        for x in tri_str:
            if x[0] <= cursor_pos <= x[1]:
                start_index = str(x[0])
                end_index = str(x[1])
                break

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
        for token, content in pygments.lex(code, self.lexer()):
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
            except Exception:
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

    def save_file(self, _=None):
        """Saves an *existing* file"""
        try:
            curr_tab = self.get_tab()
            if not self.tabs[curr_tab].file_dir:
                self.save_as()
            else:
                with open(self.tabs[curr_tab].file_dir, 'w') as file:
                    file.write(self.tabs[curr_tab].textbox.get(
                        1.0, 'end').strip())
        except:
            pass

    def new_file(self, _=None):
        """Creates a new tab(file)."""
        new_tab = ttk.Frame(self.nb)
        self.tabs[new_tab] = Document(
            new_tab, self.create_text_widget(new_tab), 'None')
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
                with open('build.bat', 'w') as f:
                    f.write((_BATCH_BUILD.format(
                        self.tabs[self.get_tab()].file_dir)))
                run_in_terminal('build.bat && exit')
            else:
                with open('build.sh', 'w') as f:
                    f.write((_BATCH_BUILD.format(
                        self.tabs[self.get_tab()].file_dir)))
                os.system('chmod 700 build.sh')
                run_in_terminal('./build.sh && exit')
        except Exception:
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

    def _del(self, _=None):
        currtext = self.tabs[self.get_tab()].textbox

    def autoindent(self, _=None):
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

    def search(self, _=None):
        global case
        global regexp
        case = 0
        regexp = 0
        search_frame = ttk.Frame(self.tabs[self.get_tab()].textbox.frame)
        style = ThemedStyle(search_frame)
        style.set_theme("black")
        self.codemenu.entryconfigure(3, state='disabled')

        search_frame.pack(anchor='nw')
        ttk.Label(search_frame, text='Search: ').pack(
            side='left', anchor='nw', fill='y')
        content = tk.Entry(search_frame, background='black',
                           foreground='white', insertbackground='white',
                           highlightthickness=0)
        content.pack(side='left', fill='both')
        content.focus_set()
        find_button = ttk.Button(search_frame, text='Highlight Matches')
        find_button.pack(side='left')
        clear_button = ttk.Button(search_frame, text='Clear Highlights')
        clear_button.pack(side='left')

        case_button = ttk.Button(search_frame, text='Case Sensitive[0]')
        case_button.pack(side='left')

        reg_button = ttk.Button(search_frame, text='RegExp[0]')
        reg_button.pack(side='left')

        def find(_=None):
            text = self.tabs[self.get_tab()].textbox
            text.tag_remove('found', '1.0', 'end')
            s = content.get()
            if s:
                idx = '1.0'
                while 1:
                    idx = text.search(s, idx, nocase=(not case),
                                      stopindex='end', regexp=(not regexp))
                    if not idx:
                        break
                    lastidx = '%s+%dc' % (idx, len(s))
                    text.tag_add('found', idx, lastidx)
                    idx = lastidx
                text.tag_config('found', foreground='red', background='yellow')

        def clear():
            text = self.tabs[self.get_tab()].textbox
            text.tag_remove('found', '1.0', 'end')

        def caseYN():
            global case
            if case == 1:
                case = 0
                case_button.config(text='Case Sensitive[0]')
            else:
                case = 1
                case_button.config(text='Case Sensitive[1]')

        def regexpYN():
            global regexp
            if regexp == 1:
                regexp = 0
                reg_button.config(text='RegExp[0]')
            else:
                regexp = 1
                reg_button.config(text='RegExp[1]')

        find_button.config(command=find)
        clear_button.config(command=clear)
        case_button.config(command=caseYN)
        reg_button.config(command=regexpYN)

        def _exit():
            search_frame.pack_forget()
            clear()
            self.tabs[self.get_tab()].textbox.focus_set()
            self.codemenu.entryconfigure(3, state='normal')

        ttk.Button(search_frame, text='x', command=_exit,
                   width=1).pack(side='right', anchor='ne')

    def undo(self, _=None):
        try:
            self.tabs[self.get_tab()].textbox.edit_undo()
        except Exception:
            pass

    def redo(self, _=None):
        try:
            self.tabs[self.get_tab()].textbox.edit_redo()
        except Exception:
            pass

    def right_click(self, event):
        self.right_click_menu.post(event.x_root, event.y_root)

    def right_click_tab(self, event):
        self.tab_right_click_menu.post(event.x_root, event.y_root)

    def close_tab(self, event=None):
        global selected_tab
        try:
            if self.nb.index("end"):
                # Close the current tab if close is selected from file menu, or
                # keyboard shortcut.
                if event is None or event.type == str(2):
                    selected_tab = self.get_tab()
                # Otherwise close the tab based on coordinates of center-click.
                else:
                    try:
                        index = event.widget.index(
                            '@%d,%d' % (event.x, event.y))
                        selected_tab = self.nb.nametowidget(
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
                    event.widget.index('@%d,%d' % (event.x, y)),
                    self.nb.select())
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

    def config(self, _=None):
        self.open_file('settings.json')

    def update_settings(self):
        self.lexer = self.settings_class.get_settings('lexer')
        self.filetypes = self.settings_class.get_settings('file_type')
        self._highlight_all()

    def lint_source(self):
        currdir = self.tabs[self.get_tab()].file_dir
        subprocess.run(f'chmod 700 lint.sh && ./lint.sh {currdir}', shell=True)
        self.open_file('results.txt')

    def goto(self, _=None):
        goto_frame = ttk.Frame(self.tabs[self.get_tab()].textbox.frame)
        style = ttkthemes.ThemedStyle(goto_frame)
        style.set_theme('black')
        goto_frame.pack(anchor='nw')
        ttk.Label(goto_frame, text='Go to place: [Ln].[Col] ').pack(
            side='left')
        place = tk.Entry(goto_frame, background='black',
                         foreground='white', insertbackground='white',
                         highlightthickness=0)
        place.focus_set()
        place.pack(side='left')

        def _goto():
            currtext = self.tabs[self.get_tab()].textbox
            currtext.mark_set('insert', place.get())
            _exit()

        def _exit():
            goto_frame.pack_forget()
            self.tabs[self.get_tab()].textbox.focus_set()

        goto_button = ttk.Button(goto_frame, command=_goto, text='>> Go to')
        goto_button.pack(side='left')
        ttk.Button(goto_frame, text='x', command=_exit,
                   width=1).pack(side='right', anchor='se')


if __name__ == '__main__':
    Editor()
