#!python3
# coding: utf-8
"""
+ =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-= +
| pyplus.py -- the editor's ONLY file                 |
| The somehow-professional editor                     |
| It's extremely small! (around 40 kB)                |
| You can visit my site for more details!             |
| +---------------------------------------------+     |
| | http://ZCG-coder.github.io/NWSOFT/PyPlusWeb |     |
| +---------------------------------------------+     |
| You can also contribute it on github!               |
| Note: Some parts are adapted from stack overflow.   |
+ =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-= +
Also, it's cross-compatible!
"""
import code
import hashlib
import io
import json
import os
import platform
import queue
import shlex
import subprocess
import sys
import threading
import tkinter as tk
import tkinter.filedialog
import tkinter.font as font
import tkinter.messagebox as messagebox
import tkinter.ttk as ttk
import traceback
from pathlib import Path
from tkinter.scrolledtext import ScrolledText

import ttkthemes
from pygments.lexers.configs import ApacheConfLexer
from pygments.lexers.configs import IniLexer
from pygments.lexers.css import CssLexer
from pygments.lexers.data import JsonLexer
from pygments.lexers.html import HtmlLexer
from pygments.lexers.html import XmlLexer
from pygments.lexers.javascript import JavascriptLexer
from pygments.lexers.python import PythonLexer
from pygments.lexers.shell import BashLexer
from pygments.lexers.special import TextLexer
from pygments.lexers.templates import HtmlPhpLexer
from pygments.styles import get_style_by_name
from ttkthemes import ThemedStyle

textchars = bytearray({7, 8, 9, 10, 12, 13, 27}
                      | set(range(0x20, 0x100)) - {0x7f})


def is_binary_string(byte):
    return bool(byte.translate(None, textchars))


_APPDIR = Path(__file__).parent
# <editor-fold desc="The constant values">
_PLTFRM = (True if sys.platform.startswith('win') else False)
_OSX = (True if sys.platform.startswith('darwin') else False)
_BATCH_BUILD = ('''#!/bin/bash
set +v
cd "{script_dir}"
python3 {dir}/measure.py start
printf "================================================\n"
{cmd} "{file}"
printf "================================================\n"
echo Program Finished With Exit Code $?
python3 {dir}/measure.py stop
echo Press enter to continue...
read -s  # This will pause the script
rm timertemp.txt
''' if not _PLTFRM else '''@echo off
title Build Results
cd "{script_dir}"
{dir}/measure.py start
echo.
echo.
echo ----------------------------------------------------
{cmd} "{file}"
echo Program Finished With Exit Code %ERRORLEVEL%
{dir}/measure.py stop
echo ----------------------------------------------------
echo.
del timertemp.txt
pause
''')  # The batch files for building.
_LINT_BATCH = ('''#!/bin/bash
{cmd} $1 > results.txt
exit
''' if not _PLTFRM else '''@echo off
{cmd} %1 > results.txt
exit''')
_MAIN_KEY = 'Command' if _OSX else 'Control'  # MacOS uses Cmd, but others uses Ctrl
_TK_VERSION = int(float(tk.TkVersion) * 10)  # Gets tkinter's _version
Spinbox = ttk.Spinbox
APPNAME = "PyPlus HexEdit"
BLOCK_WIDTH = 16
BLOCK_HEIGHT = 32
BLOCK_SIZE = BLOCK_WIDTH * BLOCK_HEIGHT
ENCODINGS = ("ASCII", "CP037", "CP850", "CP1140", "CP1252", "Latin1",
             "ISO8859_15", "Mac_Roman", "UTF-8", "UTF-8-sig", "UTF-16",
             "UTF-32")


# </editor-fold>


# <editor-fold desc="shell utility">
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


def run_in_terminal(cmd,
                    cwd=os.getcwd(),
                    env_overrides=None,
                    keep_open=True,
                    title=None):
    if env_overrides is None:
        env_overrides = {}
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


def open_system_shell(cwd, env_overrides=None):
    if env_overrides is None:
        env_overrides = {}
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
    if (directory in path.split(os.pathsep) or platform.system() == "Windows"
            and directory.lower() in path.lower().split(os.pathsep)):
        return path
    else:
        return directory + os.pathsep + path


def _run_in_terminal_in_windows(cmd,
                                cwd,
                                env,
                                keep_open,
                                title='Command Prompt'):
    if keep_open:
        # Yes, the /K argument has weird quoting. Can't explain this, but it works
        quoted_args = " ".join(
            map(lambda s: s if s == "&" else '"' + s + '"', cmd))
        cmd_line = """start {title} /D "{cwd}" /W cmd /K "{quoted_args}" """.format(
            cwd=cwd,
            quoted_args=quoted_args,
            title='"' + title + '"' if title else "")

        subprocess.Popen(cmd_line, cwd=cwd, env=env, shell=True)
    else:
        subprocess.Popen(cmd,
                         creationflags=subprocess.CREATE_NEW_CONSOLE,
                         cwd=cwd,
                         env=env)


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
            term_cmd=term_cmd, in_term_cmd=_shellquote(in_term_cmd))
    else:
        whole_cmd = "{term_cmd} -e {in_term_cmd}".format(
            term_cmd=term_cmd, in_term_cmd=_shellquote(in_term_cmd))

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

            cmds += "; export {key}={value}".format(key=key,
                                                    value=_shellquote(value))

    if cmd:
        if isinstance(cmd, list):
            cmd = " ".join(map(_shellquote, cmd))
        cmds += "; " + cmd

    if not keep_open:
        cmds += "; exit"

    # try to shorten to avoid too long line https://github.com/thonny/thonny/issues/1529

    common_prefix = os.path.normpath(sys.prefix).rstrip("/")
    cmds = ("export PYPR=" + common_prefix + " ; " +
            cmds.replace(common_prefix + "/", "$PYPR" + "/"))

    # The script will be sent to Terminal with 'do script' command, which takes a string.
    # We'll prepare an AppleScript string literal for this
    # (http://stackoverflow.com/questions/10667800/using-quotes-in-a-applescript-string):
    cmd_as_apple_script_string_literal = ('"' + cmds.replace(
        "\\", "\\\\").replace('"', '\\"').replace("$", "\\$") + '"')

    # When Terminal is not open, then do script opens two windows.
    # do script ... in window 1 would solve this, but if Terminal is already
    # open, this could run the script in existing terminal (in undesirable env on situation)
    # That's why I need to prepare two variations of the 'do script' command
    do_script_cmd1 = """		do script %s """ % cmd_as_apple_script_string_literal
    do_script_cmd2 = """		do script %s in window 1 """ % cmd_as_apple_script_string_literal

    # The whole AppleScript will be executed with osascript by giving script
    # lines as arguments. The lines containing our script need to be shell-quoted:
    quoted_cmd1 = subprocess.list2cmdline([do_script_cmd1])
    quoted_cmd2 = subprocess.list2cmdline([do_script_cmd2])

    # Now we can finally assemble the osascript command line
    cmd_line = ("osascript" +
                """ -e 'if application "Terminal" is running then ' """ +
                """ -e '	tell application "Terminal"' """ + """ -e """ +
                quoted_cmd1 + """ -e '		activate' """ +
                """ -e '	end tell' """ + """ -e 'else' """ +
                """ -e '	tell application "Terminal"' """ + """ -e """ +
                quoted_cmd2 + """ -e '		activate' """ +
                """ -e '	end tell' """ + """ -e 'end if' """)

    subprocess.Popen(cmd_line, cwd=cwd, shell=True)


def _get_linux_terminal_command():
    import shutil

    xte = shutil.which("x-terminal-emulator")
    if xte:
        if os.path.realpath(xte).endswith("/lxterminal") and shutil.which(
                "lxterminal"):
            # need to know exact program, because it needs special treatment
            return "lxterminal"
        elif os.path.realpath(xte).endswith("/terminator") and shutil.which(
                "terminator"):
            # https://github.com/thonny/thonny/issues/1129
            return "terminator"
        else:
            return "x-terminal-emulator"
    # Older konsole didn't pass on the environment
    elif shutil.which("konsole"):
        if (shutil.which("gnome-terminal")
                and "gnome" in os.environ.get("DESKTOP_SESSION", "").lower()):
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


# </editor-fold>

# HEX View

class HexView:
    def __init__(self, parent):
        """
        Copyright © 2016-20 Qtrac Ltd. All rights reserved.
        This program or module is free software: you can redistribute it and/or
        modify it under the terms of the GNU General Public License as published
        by the Free Software Foundation, either version 3 of the License, or
        (at your option) any later version. It is provided for educational
        purposes and is distributed in the hope that it will be useful, but
        WITHOUT ANY WARRANTY; without even the implied warranty of
        MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
        General Public License for more details.
        """
        self.parent = parent
        self.create_variables()
        self.create_widgets()
        self.create_layout()
        self.create_bindings()

    def create_variables(self):
        self.offset = tk.IntVar()
        self.offset.set(0)
        self.encoding = tk.StringVar()
        self.encoding.set(ENCODINGS[0])

    def create_widgets(self):
        frame = self.frame = ttk.Frame(self.parent)
        self.offsetLabel = ttk.Label(frame, text="Offset")
        self.offsetSpinbox = Spinbox(
            frame, from_=0, textvariable=self.offset, increment=BLOCK_SIZE, foreground='black')
        self.encodingLabel = ttk.Label(frame, text="Encoding", underline=0)
        self.encodingCombobox = ttk.Combobox(
            frame, values=ENCODINGS, textvariable=self.encoding, state="readonly")
        self.create_view()

    def create_view(self):
        self.viewText = tk.Text(
            self.frame,
            height=BLOCK_HEIGHT,
            width=2 + (BLOCK_WIDTH * 4),
            state='disabled')
        self.viewText.tag_configure("ascii", foreground="green")
        self.viewText.tag_configure("error", foreground="red")
        self.viewText.tag_configure("hexspace", foreground="navy")
        self.viewText.tag_configure("graybg", background="lightgray")
        yscroll = ttk.Scrollbar(self.frame, command=self.viewText.yview)
        self.viewText['yscrollcommand'] = yscroll.set
        yscroll.grid(row=1, column=7, sticky='ns')

    def create_layout(self):
        for column, widget in enumerate(
                (self.offsetLabel, self.offsetSpinbox, self.encodingLabel,
                 self.encodingCombobox)):
            widget.grid(row=0, column=column, sticky=tk.W)
        self.viewText.grid(row=1, column=0, columnspan=6, sticky='nsew')
        self.frame.grid(row=0, column=0, sticky='nsew')

    def create_bindings(self):
        self.parent.bind("<Alt-f>", lambda *args: self.offsetSpinbox.focus())
        self.parent.bind("<Alt-e>", lambda *args: self.encodingCombobox.focus())
        for variable in (self.offset, self.encoding):
            variable.trace_variable("w", self.show_block)

    def show_block(self, *_):
        self.viewText.config(state='normal')
        self.viewText.delete("1.0", "end")
        if not self.filename:
            return
        with open(self.filename, "rb") as file:
            try:
                file.seek(self.offset.get(), os.SEEK_SET)
                block = file.read(BLOCK_SIZE)
            except Exception:  # Empty offsetSpinbox
                return
        rows = [block[i:i + BLOCK_WIDTH] for i in range(0, len(block), BLOCK_WIDTH)]
        for row in rows:
            self.show_bytes(row)
            self.show_line(row)
        self.viewText.insert("end", "\n")
        self.viewText.config(state='disabled')

    def show_bytes(self, row):
        self.viewText.config(state='normal')
        for byte in row:
            tags = ()
            if byte in b"\t\n\r\v\f":
                tags = ("hexspace", "graybg")
            elif 0x20 < byte < 0x7F:
                tags = ("ascii",)
            self.viewText.insert("end", "{:02X}".format(byte), tags)
            self.viewText.insert("end", " ")
        if len(row) < BLOCK_WIDTH:
            self.viewText.insert("end", " " * (BLOCK_WIDTH - len(row)) * 3)
        self.viewText.config(state='disabled')

    def show_line(self, row):
        self.viewText.config(state='normal')
        for char in row.decode(self.encoding.get(), errors="replace"):
            tags = ()
            if char in "\u2028\u2029\t\n\r\v\f\uFFFD":
                char = "."
                tags = ("graybg" if char == "\uFFFD" else "error",)
            elif 0x20 < ord(char) < 0x7F:
                tags = ("ascii",)
            elif not 0x20 <= ord(char) <= 0xFFFF:  # Tcl/Tk limit
                char = "?"
                tags = ("error",)
            self.viewText.insert("end", char, tags)
        self.viewText.insert("end", "\n")
        self.viewText.config(state='disabled')

    def open(self, filename):
        if filename and os.path.exists(filename):
            self.parent.title("{} — {}".format(filename, APPNAME))
            size = os.path.getsize(filename)
            size = (size - BLOCK_SIZE if size > BLOCK_SIZE else size - BLOCK_WIDTH)
            self.offsetSpinbox.config(to=max(size, 0))
            self.filename = filename
            self.show_block()


# from https://gist.githubusercontent.com/olisolomons/e90d53191d162d48ac534bf7c02a50cd/raw
# /cfa19387a89fda77d20c01f634dfd044525d5c8b/python_console.py
class Pipe:
    """mock stdin stdout or stderr"""

    def __init__(self):
        self.buffer = queue.Queue()
        self.reading = False

    def write(self, data):
        self.buffer.put(data)

    def flush(self):
        pass

    def readline(self):
        self.reading = True
        line = self.buffer.get()
        self.reading = False
        return line


class Console(ttk.Frame):
    """A tkinter widget which behaves like an interpreter"""

    def __init__(self, parent, _locals=None, exit_callback=None):
        super().__init__(parent)

        self.text = ConsoleText(self, wrap=tk.WORD)
        self.text.pack(fill=tk.BOTH, expand=True)
        self.text.insert('insert', sys.version + '\n')

        self.shell = code.InteractiveConsole(_locals)

        # make the enter key call the self.enter function
        self.text.bind("<Return>", self.enter)
        self.prompt_flag = True
        self.command_running = False
        self.exit_callback = exit_callback

        # replace all input and output
        sys.stdout = Pipe()
        sys.stderr = Pipe()
        sys.stdin = Pipe()

        self.readFromPipe(sys.stdout, "stdout")
        self.readFromPipe(sys.stderr, "stderr", foreground='red')

    def prompt(self):
        """Add a '>>> ' to the console"""
        self.prompt_flag = True

    def readFromPipe(self, pipe: Pipe, tag_name, **kwargs):
        """Method for writing data from the replaced stdin and stdout to the console widget"""

        # write the >>>
        if self.prompt_flag and not sys.stdin.reading:
            self.text.prompt()
            self.prompt_flag = False

        # get data from buffer
        str_io = io.StringIO()
        while not pipe.buffer.empty():
            c = pipe.buffer.get()
            str_io.write(c)

        # write to console
        str_data = str_io.getvalue()
        if str_data:
            self.text.write(str_data, "prompt_end")

        # loop
        self.after(50, lambda: self.readFromPipe(pipe, tag_name, **kwargs))

    def enter(self, _):
        """The <Return> key press handler"""

        if sys.stdin.reading:
            # if stdin requested, then put data in stdin instead of running a new command
            line = self.text.consume_last_line()
            line = line[1:] + '\n'
            sys.stdin.buffer.put(line)
            return

        # don't run multiple commands simultaneously
        if self.command_running:
            return

        # get the command text
        command = self.text.read_last_line()
        try:
            # compile it
            compiled = code.compile_command(command)
            is_complete_command = compiled is not None
        except (SyntaxError, OverflowError, ValueError):
            # if there is an error compiling the command, print it to the console
            self.text.consume_last_line()
            self.prompt()
            traceback.print_exc(0)
            return

        # if it is a complete command
        if is_complete_command:
            # consume the line and run the command
            self.text.consume_last_line()
            self.prompt()

            self.command_running = True

            def run_command():
                try:
                    self.shell.runcode(compiled)
                except SystemExit:
                    self.after(0, self.exit_callback)

                self.command_running = False

            threading.Thread(target=run_command).start()


class ConsoleText(ScrolledText):
    """
    A Text widget which handles some application logic,
    e.g. having a line of input at the end with everything else being un-editable
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # make edits that occur during on_text_change not cause it to trigger again
        def on_modified(event):
            flag = self.edit_modified()
            if flag:
                self.after(10, self.on_text_change(event))
            self.edit_modified(False)

        self.bind("<<Modified>>", on_modified)

        # store info about what parts of the text have what colour
        # used when colour info is lost and needs to be re-applied
        self.console_tags = []

        # the position just before the prompt (>>>)
        # used when inserting command output and errors
        self.mark_set("prompt_end", 1.0)

        # keep track of where user input/commands start and the committed text ends
        self.committed_hash = None
        self.committed_text_backup = ""
        self.commit_all()

    def prompt(self):
        """Insert a prompt"""
        self.mark_set("prompt_end", 'end-1c')
        self.mark_gravity("prompt_end", tk.LEFT)
        self.write(">>> ")
        self.mark_gravity("prompt_end", tk.RIGHT)

    def commit_all(self):
        """Mark all text as committed"""
        self.commit_to('end-1c')

    def commit_to(self, pos):
        """Mark all text up to a certain position as committed"""
        if self.index(pos) in (self.index("end-1c"), self.index("end")):
            # don't let text become un-committed
            self.mark_set("committed_text", "end-1c")
            self.mark_gravity("committed_text", tk.LEFT)
        else:
            # if text is added before the last prompt (">>> "), update the stored position of the tag
            for i, (tag_name, _,
                    _) in reversed(list(enumerate(self.console_tags))):
                if tag_name == "prompt":
                    tag_ranges = self.tag_ranges("prompt")
                    self.console_tags[i] = ("prompt", tag_ranges[-2],
                                            tag_ranges[-1])
                    break

        # update the hash and backup
        self.committed_hash = self.get_committed_text_hash()
        self.committed_text_backup = self.get_committed_text()

    def get_committed_text_hash(self):
        """Get the hash of the committed area -
        used for detecting an attempt to edit it"""
        return hashlib.md5(self.get_committed_text().encode()).digest()

    def get_committed_text(self):
        """Get all text marked as committed"""
        return self.get(1.0, "committed_text")

    def write(self, string, pos='end-1c'):
        """Write some text to the console"""

        # insert the text
        self.insert(pos, string)
        self.see(tk.END)

        # commit text
        self.commit_to(pos)

    def on_text_change(self, _):
        """If the text is changed, check if the change is part of the committed
        # text, and if it is revert the change"""
        if self.get_committed_text_hash() != self.committed_hash:
            # revert change
            self.mark_gravity("committed_text", tk.RIGHT)
            self.replace(1.0, "committed_text", self.committed_text_backup)
            self.mark_gravity("committed_text", tk.LEFT)

            # re-apply colours
            for tag_name, _start, _end in self.console_tags:
                self.tag_add(tag_name, _start, _end)

    def read_last_line(self):
        """Read the user input, i.e. everything written after the committed text"""
        return self.get("committed_text", "end-1c")

    def consume_last_line(self):
        """Read the user input as in read_last_line, and mark it is committed"""
        line = self.read_last_line()
        self.commit_all()
        return line


class EditorErr(Exception):
    """A nice exception class for debugging"""

    def __init__(self, message):
        # The error (e+m)
        super().__init__(
            'An editor error is occurred.' if not message else message)


class Settings:
    """A class to read data to/from settings.json"""

    def __init__(self):
        with open('settings.json') as f:
            self.settings = json.load(f)
        self.theme = self.settings['theme']
        self.highlight_theme = self.settings['pygments']
        self.font = self.settings['font'].split()[0]
        self.size = self.settings['font'].split()[1]
        self.filetype = self.settings['file_types']

    def get_settings(self, setting):
        if setting == 'font':
            return f'{self.font} {self.size}'
        elif setting == 'theme':
            return self.theme
        elif setting == 'pygments':
            return self.highlight_theme
        elif setting == 'file_type':
            # Always starts with ('All files', '*.* *')
            if self.filetype == 'all':
                return (('All files', '*.* *'),)
            elif self.filetype == 'py':
                # Extend this list, since Python has a lot of file types
                return ('All files',
                        '*.* *'), ('Python Files',
                                   '*.py *.pyw *.pyx *.py3 *.pyi'),
            elif self.filetype == 'txt':
                return ('All files', '*.* *'), ('Text documents',
                                                '*.txt *.rst'),
            elif self.filetype == 'xml':
                # Extend this, since xml has a lot of usage formats
                return ('All files', '*.* *'), ('XML',
                                                '*.xml *.plist *.iml *.rss'),
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
                bold = font.Font(family=self.textwidget['font'], weight='bold')
                self.create_text(2,
                                 y,
                                 anchor="nw",
                                 text=linenum,
                                 fill='black',
                                 font=bold)
            else:
                self.create_text(2,
                                 y,
                                 anchor="nw",
                                 text=linenum,
                                 fill='black',
                                 font=self.textwidget['font'])
            i = self.textwidget.index("%s+1line" % i)


class EnhancedText(tk.Text):
    """Text widget, but 'records' your key actions
    If you hit a key, or the text widget's content has changed,
    it generats an event, to redraw the line numbers."""

    def __init__(self, *args, **kwargs):
        tk.Text.__init__(self, *args, **kwargs)

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
            if (args[0] in ("insert", "replace", "delete")
                    or args[0:3] == ("mark", "set", "insert")
                    or args[0:2] == ("xview", "moveto")
                    or args[0:2] == ("xview", "scroll")
                    or args[0:2] == ("yview", "moveto")
                    or args[0:2] == ("yview", "scroll")):
                self.event_generate("<<Change>>", when="tail")

            # return what the actual widget returned

            return result
        except Exception:
            pass


class EnhancedTextFrame(ttk.Frame):
    """An enhanced text frame to put the
    text widget with linenumbers in."""

    def __init__(self, *args, **kwargs):
        ttk.Frame.__init__(self, *args, **kwargs)
        settings_class = Settings()
        self.font = settings_class.get_settings('font')
        self.text = EnhancedText(self,
                                 bg='black',
                                 fg='white',
                                 insertbackground='white',
                                 selectforeground='black',
                                 selectbackground='white',
                                 highlightthickness=0,
                                 font=self.font,
                                 wrap='none')
        self.linenumbers = TextLineNumbers(self,
                                           width=30,
                                           bg='gray',
                                           bd=0,
                                           highlightthickness=0)
        self.linenumbers.attach(self.text)
        self.linenumbers.pack(side="left", fill="y")
        yscroll = ttk.Scrollbar(self, command=self.text.yview)
        self.text['yscrollcommand'] = yscroll.set
        yscroll.pack(side='right', fill='y')
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
        except Exception:
            pass

    def __initialize_custom_style(self):
        style = ttk.Style()
        self.images = (tk.PhotoImage("img_close",
                                     data='''iVBORw0KGgoAAAANSUhEUgAAACAAAAAgA
            gMAAAAOFJJnAAAAAXNSR0IB2cksfwAAAAlwSFlzAAALEwAACxMBAJqcGAAAAAxQTFRFA
            AAAAAAA/yYA////nxJg7AAAAAR0Uk5TAP///7MtQIgAAACMSURBVHicPZC9AQMhCIVJk
            yEyTZbIEnfLZIhrTgtHYB9HoIB7/CiFfArCA6JfGNGrhX3pnfCnT3i+6BQHu+lU+O5gg
            KE3HTaRIgBGkk3AUKQ0AE4wAO+IOrDwDBiKCg7dNKGZFPCCFepWyfg1Vx2pytkCvbIpr
            inDq4QwV5hSS/yhNc4ecI+8l7DW8gDYFaqpCCFJsQAAAABJRU5ErkJggg==
                '''),
                       tk.PhotoImage("img_closeactive",
                                     data='''iVBORw0KGgoAAAANSUhEUgAAACA
            AAAAgBAMAAACBVGfHAAAAAXNSR0IB2cksfwAAAAlwSFlzAAALEwAACxMBAJqcGAAAAA9
            QTFRFAAAAAAAA/YAI////////uHhEXgAAAAV0Uk5TAP///zOOAqjJAAAAk0lEQVR4nGW
            S2RGAMAhE44wFaDow6SD035scCwMJHxofyxGwtfYma2zXSPYw6Bl8VTCJJZ2fbkQsYbB
            CAEAhWAL07QIFLlGHAEiMK7CjYQV6RqAB+UB1AyJBZgCWoDYAS2gUMHewh0iOklSrpLL
            WR2pMval1c6bLITyu7z3EgLyFNMI65BFTtzUcizpWeS77rr/DDzkRRQdj40f8AAAAAEl
            FTkSuQmCC
                '''),
                       tk.PhotoImage("img_closepressed",
                                     data='''iVBORw0KGgoAAAANSUhEUgAAAC
            AAAAAgAgMAAAAOFJJnAAAAAXNSR0IB2cksfwAAAAlwSFlzAAALEwAACxMBAJqcGAAAAA
            xQTFRFAAAAAAAA//8K////dEqdoAAAAAR0Uk5TAP///7MtQIgAAACMSURBVHicPZC9AQ
            MhCIVJkyEyTZbIEnfLZIhrTgtHYB9HoIB7/CiFfArCA6JfGNGrhX3pnfCnT3i+6BQHu+
            lU+O5ggKE3HTaRIgBGkk3AUKQ0AE4wAO+IOrDwDBiKCg7dNKGZFPCCFepWyfg1Vx2pyt
            kCvbIprinDq4QwV5hSS/yhNc4ecI+8l7DW8gDYFaqpCCFJsQAAAABJRU5ErkJggg==
            '''))  # The images, 32x32-sized

        style.element_create(
            "close",
            "image",
            "img_close",
            ("active", "pressed", "!disabled", "img_closepressed"),
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

    def __init__(self, _, TextWidget, FileDir):
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
        self.theme = self.settings_class.get_settings('theme')
        self.master = ttkthemes.ThemedTk()
        self.master.minsize(900, 600)
        style = ThemedStyle(self.master)
        style.set_theme(self.theme)  # Apply ttkthemes to master window.
        self.master.geometry("600x400")
        self.master.title('PyPlus')
        self.master.iconphoto(
            True,
            tk.PhotoImage(data='''iVBORw0KGgoAAAANSUhEU
                gAAACAAAAAgBAMAAACBVGfHAAAAAXNSR0IB2cksfwAAAAlwSFlzAAASdAAAEnQB3mYfeAAA
                ABJQTFRFAAAAAAAA////TWyK////////WaqEwgAAAAZ0Uk5TAP8U/yr/h0gXnQAAAHpJREF
                UeJyNktENgCAMROsGog7ACqbpvzs07L+KFCKWFg0XQtLHFQIHAEBoiiAK2BSkXlBpzWDX4D
                QGsRhw9B3SMwNSSj1glNEDqhUpUGw/gMuUd+d2Csny6xgAZB4A1IDwG1SxAc/95t7DAPPIm
                4/BBeWjdGHr73AB3CCCXSvLODzvAAAAAElFTkSuQmCC'''))
        # Base64 image, this probably decreases the repo size.

        self.filetypes = self.settings_class.get_settings('file_type')

        self.tabs = {}

        self.nb = CustomNotebook(self.master, self.close_tab)
        self.nb.bind('<B1-Motion>', self.move_tab)
        self.nb.pack(expand=1, fill='both')
        self.nb.enable_traversal()

        self.master.protocol(
            'WM_DELETE_WINDOW', self.exit
        )  # When the window is closed, or quit from Mac, do exit action

        menubar = tk.Menu(self.master)
        # Name can be apple only, don't really know why!
        app_menu = tk.Menu(menubar, name='apple', tearoff=0)

        app_menu.add_command(label='About PyPlus', command=self._version)

        if _TK_VERSION < 85 or not _OSX:
            app_menu.add_command(label="Preferences...", command=self.config)
            app_menu.add_separator()
            app_menu.add_command(label='Exit Editor', command=self.exit)
        else:
            self.master.createcommand('tk::mac::ShowPreferences',
                                      self.config)  # OS X
        app_menu.add_command(label='Restart app', command=self.restart)

        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label='New Tab',
                             command=self.new_file,
                             accelerator=f'{_MAIN_KEY}-n')
        filemenu.add_command(label='Open File',
                             command=self.open_file,
                             accelerator=f'{_MAIN_KEY}-o')
        filemenu.add_command(label='Close Tab',
                             command=self.close_tab,
                             accelerator=f'{_MAIN_KEY}-w')
        filemenu.add_command(label='Reload from disk', command=self.reload)

        editmenu = tk.Menu(menubar, tearoff=0)
        editmenu.add_command(label='Undo',
                             command=self.undo,
                             accelerator=f'{_MAIN_KEY}-z')
        editmenu.add_command(label='Redo',
                             command=self.redo,
                             accelerator=f'{_MAIN_KEY}-Shift-z')
        editmenu.add_separator()
        editmenu.add_command(label='Cut',
                             command=self.cut,
                             accelerator=f'{_MAIN_KEY}-x')
        editmenu.add_command(label='Copy',
                             command=self.copy,
                             accelerator=f'{_MAIN_KEY}-c')
        editmenu.add_command(label='Paste',
                             command=self.paste,
                             accelerator=f'{_MAIN_KEY}-v')
        editmenu.add_command(label='Delete Selected', command=self.delete)
        editmenu.add_command(label='Select All',
                             command=self.select_all,
                             accelerator=f'{_MAIN_KEY}-a')

        self.codemenu = tk.Menu(menubar, tearoff=0)
        self.codemenu.add_command(label='Build',
                                  command=self.build,
                                  accelerator=f'{_MAIN_KEY}-b')
        self.codemenu.add_command(label='Lint', command=self.lint_source)
        self.codemenu.add_command(label='Auto-format', command=self.autopep)
        self.codemenu.add_separator()
        self.codemenu.add_command(label='Find and replace',
                                  command=self.search,
                                  accelerator=f'{_MAIN_KEY}-f')
        self.codemenu.add_separator()
        self.codemenu.add_command(label='Open Python Shell',
                                  command=self.open_shell)

        navmenu = tk.Menu(menubar, tearoff=0)
        navmenu.add_command(label='Go to ...',
                            command=self.goto,
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
        self.right_click_menu.add_command(label='Select All',
                                          command=self.select_all)

        self.tab_right_click_menu = tk.Menu(self.master, tearoff=0)
        self.tab_right_click_menu.add_command(label='New Tab',
                                              command=self.new_file)
        self.tab_right_click_menu.add_command(label='Close Tab',
                                              command=self.close_tab)
        self.nb.bind(('<Button-2>' if _OSX else '<Button-3>'),
                     self.right_click_tab)
        # Mouse bindings
        first_tab = ttk.Frame(self.nb)
        self.tabs[first_tab] = Document(first_tab,
                                        self.create_text_widget(first_tab),
                                        FileDir='None')
        self.nb.add(first_tab, text='None')
        self.mouse()
        self.master.after(0, self.update_settings)

        def tab(_=None):
            self.tabs[self.get_tab()].textbox.insert(
                'insert', ' ' * 4)  # Convert tabs to spaces
            return 'break'  # Quit quickly, before a char is being inserted.

        # Keyboard bindings
        self.master.bind(f'<{_MAIN_KEY}-w>', self.close_tab)
        self.master.bind(f'<{_MAIN_KEY}-o>', self._open)
        self.master.bind(f'<{_MAIN_KEY}-b>', self.build)
        self.master.bind(f'<{_MAIN_KEY}-f>', self.search)
        self.master.bind(f'<{_MAIN_KEY}-n>', self.new_file)
        self.master.bind(f'<{_MAIN_KEY}-N>', self.goto)
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
        textbox.lexer = PythonLexer()
        textbox.lint_cmd = 'pylint'
        textbox.bind('<Return>', self.autoindent)
        textbox.bind("<<KeyEvent>>", self.key)
        textbox.bind("<<MouseEvent>>", self.mouse)
        textbox.event_add("<<KeyEvent>>", "<KeyRelease>")
        textbox.event_add("<<MouseEvent>>", "<ButtonRelease>")
        textbox.statusbar = ttk.Label(frame,
                                      text='PyPlus',
                                      justify='right',
                                      anchor='e')
        textbox.statusbar.pack(side='bottom', fill='x', anchor='e')
        textbox.bind(('<Button-2>' if _OSX else '<Button-3>'),
                     self.right_click)

        self.master.geometry('1000x600')  # Configure window size
        textbox.focus_set()
        return textbox

    def settitle(self, _=None):
        if len(self.tabs) == 0:
            return
        self.master.title(f'PyPlus -- {self.tabs[self.get_tab()].file_dir}')

    def key(self, event=None):
        """Event when a key is pressed."""
        if len(self.tabs) == 0:
            return
        currtext = self.tabs[self.get_tab()].textbox
        try:
            self.create_tags()
            self.recolorize()
            currtext.statusbar.config(
                text=f'PyPlus | file {self.nb.tab(self.get_tab())["text"]}| ln {int(float(currtext.index("insert")))}'
                     f' | col {str(int(currtext.index("insert").split(".")[1:][0]))}'
            )
            # Update statusbar and titlebar
            self.settitle()
            # Auto-save
            if event.char and event.keysym not in ('Left', 'Right', 'Up',
                                                   'Down'):
                self.save_file()
        except Exception:
            currtext.statusbar.config(text='PyPlus')  # When error occurs

    def mouse(self, _=None):
        """The action done when the mouse is clicked"""
        if len(self.tabs) == 0:
            return
        currtext = self.tabs[self.get_tab()].textbox
        try:
            currtext.statusbar.config(
                text=f"PyPlus | file {self.nb.tab(self.get_tab())['text']}| ln {int(float(currtext.index('insert')))} "
                     f"| col {str(int(currtext.index('insert').split('.')[1:][0]))}"
            )
            # Update statusbar and titlebar
            self.settitle()
        except Exception:
            currtext.statusbar.config(text=f'PyPlus')  # When error occurs

    def create_tags(self):
        """
            the method creates the tags associated with each distinct style element of the
            source code 'dressing'
        """
        if len(self.tabs) == 0:
            return
        currtext = self.tabs[self.get_tab()].textbox
        bold_font = font.Font(currtext, currtext.cget("font"))
        bold_font.configure(weight=font.BOLD)
        italic_font = font.Font(currtext, currtext.cget("font"))
        italic_font.configure(slant=font.ITALIC)
        bold_italic_font = font.Font(currtext, currtext.cget("font"))
        bold_italic_font.configure(weight=font.BOLD, slant=font.ITALIC)
        style = get_style_by_name(self.settings_class.get_settings('pygments'))

        for ttype, ndef in style:
            tag_font = None

            if ndef['bold'] and ndef['italic']:
                tag_font = bold_italic_font
            elif ndef['bold']:
                tag_font = bold_font
            elif ndef['italic']:
                tag_font = italic_font

            if ndef['color']:
                foreground = "#%s" % ndef['color']
            else:
                foreground = None

            currtext.tag_configure(str(ttype),
                                   foreground=foreground,
                                   font=tag_font)

    def recolorize(self):
        """
            this method colors and styles the prepared tags
        """
        if len(self.tabs) == 0:
            return
        currtext = self.tabs[self.get_tab()].textbox
        _code = currtext.get("1.0", "end-1c")
        tokensource = currtext.lexer.get_tokens(_code)
        start_line = 1
        start_index = 0
        end_line = 1
        end_index = 0

        for ttype, value in tokensource:
            if "\n" in value:
                end_line += value.count("\n")
                end_index = len(value.rsplit("\n", 1)[1])
            else:
                end_index += len(value)

            if value not in (" ", "\n"):
                index1 = "%s.%s" % (start_line, start_index)
                index2 = "%s.%s" % (end_line, end_index)

                for tagname in currtext.tag_names(index1):
                    if tagname != 'sel':
                        currtext.tag_remove(tagname, index1, index2)

                currtext.tag_add(str(ttype), index1, index2)

            start_line = end_line
            start_index = end_index
            currtext.tag_configure('sel', foreground='black')

    def open_file(self, file=''):
        """Opens a file
        If a file is not provided, a messagebox'll
        pop up to ask the user to select the path.
        """
        if not file:
            file_dir = (tkinter.filedialog.askopenfilename(
                master=self.master,
                initialdir='/',
                title='Select file',
                filetypes=self.filetypes))
        else:
            file_dir = file

        if file_dir:
            try:  # If the file is in binary, ask the user to open in Hex editor
                if is_binary_string(open(file_dir, 'rb').read(1024)):
                    if messagebox.askyesno(
                            'Error',
                            'This file is in binary format, \n'
                            'which this editor does not edit. \n'
                            'Would you like to view it in Hex Editor?\n'
                    ):
                        app = tk.Toplevel(self.master)
                        ttkthemes.ThemedStyle(app).set_theme(self.theme)
                        app.transient(self.master)
                        app.title(APPNAME)
                        window = HexView(app)
                        window.open(file_dir)
                        app.resizable(width=False, height=False)
                        app.mainloop()
                    else:
                        return
                file = open(file_dir)
                extens = file_dir.split('.')[-1]

                new_tab = ttk.Frame(self.nb)
                self.tabs[new_tab] = Document(new_tab,
                                              self.create_text_widget(new_tab),
                                              file_dir)
                self.nb.add(new_tab, text=os.path.basename(file_dir))
                self.nb.select(new_tab)

                # Puts the contents of the file into the text widget.
                currtext = self.tabs[new_tab].textbox
                currtext.insert('end', file.read().replace('\t', ' ' * 4))
                # Inserts file content, replacing tabs with four spaces
                currtext.focus_set()
                self.mouse()
                if extens == 'py' or extens == 'pyw' or extens == 'jy' or extens == 'sage' or extens == 'sc' \
                        or extens == 'SConstruct' or extens == 'SConscript' or extens == 'bzl' or extens == 'BUCK' \
                        or extens == 'BUILD' or file_dir == 'BUILD.bazel' or extens == 'WORKSPACE' or extens == 'tac':
                    currtext.lexer = (PythonLexer())
                    currtext.cmd = 'python3'
                    currtext.lint_cmd = "pylint"
                elif extens == "txt" or extens == "text":
                    currtext.lexer = (TextLexer())
                    currtext.cmd = 'more'
                    currtext.lint_cmd = None
                elif extens == "htm" or extens == "html" or extens == 'xhtml':
                    currtext.lexer = (HtmlLexer())
                    if _PLTFRM:
                        currtext.cmd = 'start'
                    elif _OSX:
                        currtext.cmd = 'open -a Safari'
                    else:
                        currtext.cmd = 'xdg-open'
                    currtext.lint_cmd = 'html_lint.py'
                elif extens == "xml" or extens == "xsl" or extens == "rss" or extens == "xslt" or extens == "xsd" or \
                        extens == "wsdl" or extens == "wsf":
                    currtext.lexer = (XmlLexer())
                    currtext.cmd = 'more'
                    currtext.lint_cmd = None  # I haven't found any XML linters written in Python
                elif extens == "php" or extens == "php5":
                    currtext.lexer = (HtmlPhpLexer())
                    if _PLTFRM:
                        currtext.cmd = 'start'
                    elif _OSX:
                        os.system('phplint/bin/phplint')
                        currtext.cmd = 'open -a Safari'
                        currtext.lint_cmd = 'phplint/bin/phplint'
                    else:
                        os.system('phplint/bin/phplint')
                        currtext.cmd = 'xdg-open'
                        currtext.lint_cmd = 'phplint/bin/phplint'
                elif extens == "ini" or extens == "init":
                    currtext.lexer = (IniLexer())
                    currtext.cmd = 'more'
                    currtext.lint_cmd = None
                elif extens == "conf" or extens == "cnf" or extens == "config":
                    currtext.lexer = (ApacheConfLexer())
                    currtext.cmd = 'more'
                    currtext.lint_cmd = None
                elif extens == 'sh' or extens == 'ksh' or extens == 'bash' or extens == 'ebuild' or extens == 'eclass' \
                        or extens == 'exheres-0' or extens == 'exlib' or extens == 'zsh' or extens == 'bashrc' \
                        or extens == 'PKGBUILD':
                    currtext.lexer = (BashLexer())
                    currtext.cmd = 'bash'
                    currtext.lint_cmd = None

                elif extens == "json":
                    currtext.lexer = (JsonLexer())
                    currtext.cmd = 'more'
                    currtext.lint_cmd = None
                elif extens == 'js' or extens == 'javascript':
                    currtext.lexer = (JavascriptLexer())
                    currtext.cmd = 'node'
                    currtext.lint_cmd = None
                elif extens == 'css':
                    currtext.lexer = (CssLexer())
                    currtext.cmd = 'more'
                    currtext.lint_cmd = None
                else:
                    currtext.lexer = (TextLexer())
                    currtext.cmd = 'more'
                    currtext.lint_cmd = None
                self.create_tags()
                self.recolorize()
                return 'break'
            except Exception as e:
                print(str(e))

    def _open(self, _=None):
        """This method just prompts the user to open a file when C-O is pressed"""
        self.open_file()

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
            self.tabs[curr_tab].file_dir = os.path.basename(file_dir)
            self.nb.tab(curr_tab, text=self.tabs[curr_tab].file_dir)
            file = open(file_dir, 'w')
            file.write(self.tabs[curr_tab].textbox.get(1.0, 'end'))
            file.close()

    def save_file(self, _=None):
        """Saves an *existing* file"""
        try:
            curr_tab = self.get_tab()
            if self.tabs[curr_tab].file_dir == 'None':
                self.save_as()
                return
            with open(self.tabs[curr_tab].file_dir, 'w') as file:
                file.write(self.tabs[curr_tab].textbox.get(1.0, 'end').strip())
        except Exception:
            pass

    def new_file(self, _=None):
        """Creates a new tab(file)."""
        new_tab = ttk.Frame(self.nb)
        self.tabs[new_tab] = Document(new_tab,
                                      self.create_text_widget(new_tab), 'None')
        self.nb.add(new_tab, text='None')
        self.nb.select(new_tab)

    def copy(self):
        try:
            sel = self.tabs[self.get_tab()].textbox.get(
                tk.SEL_FIRST, tk.SEL_LAST)
            self.tabs[self.get_tab()].textbox.clipboard_clear()
            self.tabs[self.get_tab()].textbox.clipboard_append(sel)
        except Exception:
            pass

    def delete(self):
        try:
            self.tabs[self.get_tab()].textbox.delete(tk.SEL_FIRST, tk.SEL_LAST)
            self.key()
        except Exception:
            pass

    def cut(self, textbox=None):
        try:
            currtext = self.tabs[self.get_tab()].textbox
            sel = currtext.get(tk.SEL_FIRST, tk.SEL_LAST)
            textbox.clipboard_clear()
            textbox.clipboard_append(sel)
            currtext.delete(tk.SEL_FIRST, tk.SEL_LAST)
            self.key()
        except Exception:
            pass

    def paste(self):
        try:
            self.tabs[self.get_tab()].textbox.insert(
                tk.INSERT, self.tabs[self.get_tab()].textbox.clipboard_get())
        except Exception:
            pass

    def select_all(self, _=None):
        try:
            curr_tab = self.get_tab()
            self.tabs[curr_tab].textbox.tag_add(tk.SEL, '1.0', tk.END)
            self.tabs[curr_tab].textbox.mark_set(tk.INSERT, tk.END)
            self.tabs[curr_tab].textbox.see(tk.INSERT)
        except Exception:
            pass

    def build(self, _=None):
        """Builds the file
        Steps:
        1) Writes build code into the batch file.
        2) Linux only: uses chmod to make the sh execuable
        3) Runs the build file"""
        try:
            if _PLTFRM:  # Windows
                with open('./build.bat', 'w') as f:
                    f.write((_BATCH_BUILD.format(
                        dir=_APPDIR,
                        file=self.tabs[self.get_tab()].file_dir,
                        cmd=self.tabs[self.get_tab()].textbox.cmd)))
                run_in_terminal('build.bat && exit && del build.bat')
            else:
                with open('./build.sh', 'w') as f:
                    f.write((_BATCH_BUILD.format(
                        dir=_APPDIR,
                        file=self.tabs[self.get_tab()].file_dir,
                        cmd=self.tabs[self.get_tab()].textbox.cmd,
                        script_dir=Path(self.tabs[self.get_tab()].file_dir).parent)))
                os.system('chmod 700 build.sh')
                run_in_terminal('./build.sh && exit && rm build.sh')
        except Exception:
            messagebox.showerror('Error',
                                 'Terminal emulator cannot be detected.')

    def open_shell(self):
        root = tk.Toplevel()
        root.title('Python Shell')
        ttkthemes.ThemedStyle(root).set_theme(self.theme)
        main_window = Console(root, None, root.destroy)
        main_window.pack(fill=tk.BOTH, expand=True)
        root.mainloop()

    def autoinsert(self, event=None):
        """Auto-inserts a symbol
        * ' -> ''
        * " -> ""
        * ( -> ()
        * [ -> []
        * { -> {}"""
        if len(self.tabs) == 0:
            return
        currtext = self.tabs[self.get_tab()].textbox
        # Strings
        if event.char not in ['(', '[', '{']:
            currtext.insert('insert', event.char)
            currtext.mark_set(
                'insert', '%d.%s' %
                          (int(float(currtext.index('insert'))),
                           str(int(currtext.index('insert').split('.')[1:][0]) - 1)))
            self.key()
        # Others
        elif event.char == '(':
            currtext.insert('insert', ')')
            currtext.mark_set(
                'insert', '%d.%s' %
                          (int(float(currtext.index('insert'))),
                           str(int(currtext.index('insert').split('.')[1:][0]) - 1)))
            return 'break'
        elif event.char == '[':
            currtext.insert('insert', ']')
            currtext.mark_set(
                'insert', '%d.%s' %
                          (int(float(currtext.index('insert'))),
                           str(int(currtext.index('insert').split('.')[1:][0]) - 1)))
            return 'break'
        elif event.char == '{':
            currtext.insert('insert', '}')
            currtext.mark_set(
                'insert', '%d.%s' %
                          (int(float(currtext.index('insert'))),
                           str(int(currtext.index('insert').split('.')[1:][0]) - 1)))
            return 'break'

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
        if 'return' in linetext or 'break' in linetext:
            indentation = indentation[4:]
        if linetext.endswith('(') or linetext.endswith(
                ', ') or linetext.endswith(','):
            indentation += " " * 4

        currtext.insert(currtext.index("insert"), "\n" + indentation)
        self.key()
        return "break"

    def search(self, _=None):
        global case
        global regexp
        global start, end
        if len(self.tabs) == 0:
            return
        case = 0
        regexp = 0
        start = tk.FIRST if not tk.SEL_FIRST else tk.SEL_FIRST
        end = tk.END if not tk.SEL_LAST else tk.SEL_LAST
        search_frame = ttk.Frame(self.tabs[self.get_tab()].textbox.frame)
        style = ThemedStyle(search_frame)
        style.set_theme(self.theme)
        self.codemenu.entryconfigure(3, state='disabled')

        search_frame.pack(anchor='nw')
        ttk.Label(search_frame, text='Search: ').pack(side='left',
                                                      anchor='nw',
                                                      fill='y')
        content = tk.Entry(search_frame,
                           background='black',
                           foreground='white',
                           insertbackground='white',
                           highlightthickness=0)
        content.pack(side='left', fill='both')

        ttk.Label(search_frame, text='Replacement: ').pack(side='left',
                                                           anchor='nw',
                                                           fill='y')
        repl = tk.Entry(search_frame,
                        background='black',
                        foreground='white',
                        insertbackground='white',
                        highlightthickness=0)
        repl.pack(side='left', fill='both')

        find_button = ttk.Button(search_frame, text='Highlight All')
        find_button.pack(side='left')
        clear_button = ttk.Button(search_frame, text='Clear All')
        clear_button.pack(side='left')

        case_button = ttk.Button(search_frame, text='Case Sensitive[0]')
        case_button.pack(side='left')

        reg_button = ttk.Button(search_frame, text='RegExp[0]')
        reg_button.pack(side='left')

        repl_button = ttk.Button(search_frame, text='Replace all')
        repl_button.pack(side='left')

        def find(_=None):
            text = self.tabs[self.get_tab()].textbox
            text.tag_remove('found', '1.0', 'end')
            s = content.get()
            if s:
                idx = '1.0'
                while 1:
                    idx = text.search(s,
                                      idx,
                                      nocase=(not case),
                                      stopindex='end',
                                      regexp=(not regexp))
                    if not idx:
                        break
                    lastidx = '%s+%dc' % (idx, len(s))
                    text.tag_add('found', idx, lastidx)
                    idx = lastidx
                text.tag_config('found', foreground='red', background='yellow')

        def replace():
            text = self.tabs[self.get_tab()].textbox
            text.tag_remove('found', '1.0', 'end')
            s = content.get()
            r = repl.get()
            if s:
                idx = '1.0'
                while 1:
                    idx = text.search(s,
                                      idx,
                                      nocase=(not case),
                                      stopindex='end',
                                      regexp=(not regexp))
                    if not idx:
                        break
                    lastidx = '%s+%dc' % (idx, len(s))
                    text.delete(idx, lastidx)
                    text.insert(idx, r)
                    idx = lastidx

        def clear():
            text = self.tabs[self.get_tab()].textbox
            text.tag_remove('found', '1.0', 'end')

        def case_yn():
            global case
            if case == 1:
                case = 0
                case_button.config(text='Case Sensitive[0]')
            else:
                case = 1
                case_button.config(text='Case Sensitive[1]')

        def regexp_yn():
            global regexp
            if regexp == 1:
                regexp = 0
                reg_button.config(text='RegExp[0]')
            else:
                regexp = 1
                reg_button.config(text='RegExp[1]')

        find_button.config(command=find)
        clear_button.config(command=clear)
        case_button.config(command=case_yn)
        reg_button.config(command=regexp_yn)
        repl_button.config(command=replace)

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
                        index = event.widget.index('@%d,%d' %
                                                   (event.x, event.y))
                        selected_tab = self.nb.nametowidget(
                            self.nb.tabs()[index])
                    except tk.TclError:
                        return

            self.nb.forget(selected_tab)
            self.tabs.pop(selected_tab)
            self.mouse()
        except Exception:
            pass

    def reload(self):
        if len(self.tabs) == 0:
            return
        file_dir = self.tabs[self.get_tab()].file_dir
        if file_dir == 'None':
            self.close_tab()
            self.new_file()
            return
        self.close_tab()
        self.open_file(file_dir)

    def exit(self, force=False):
        if not force:
            self.master.destroy()
        else:
            sys.exit(0)

    def restart(self):
        self.exit()
        self.__init__()

    def get_tab(self):
        return self.nb.nametowidget(self.nb.select())

    def move_tab(self, event):
        if self.nb.index('end') > 1:
            y = self.get_tab().winfo_y() - 5

            try:
                self.nb.insert(event.widget.index('@%d,%d' % (event.x, y)),
                               self.nb.select())
            except tk.TclError:
                return

    def _version(self):
        """Shows the _version and related info of the editor."""
        ver = tk.Toplevel()
        style = ThemedStyle(ver)
        style.set_theme(self.theme)  # Applies the ttk theme
        ver.geometry('480x190')
        ver.resizable(0, 0)
        ver.transient(self.master)
        cv = tk.Canvas(ver)
        cv.pack(fill='both', expand=1)
        img = tk.PhotoImage(file='ver.gif')
        cv.create_image(0, 0, anchor='nw', image=img)
        ver.mainloop()

    def config(self, _=None):
        self.open_file('settings.json')

    def update_settings(self):
        self.filetypes = self.settings_class.get_settings('file_type')
        self.create_tags()
        self.recolorize()

    def lint_source(self):
        if len(self.tabs) == 0:
            return
        if self.tabs[self.get_tab()].textbox.lint_cmd:
            currdir = self.tabs[self.get_tab()].file_dir
            if _PLTFRM:
                with open('lint.bat', 'w') as f:
                    f.write(
                        _LINT_BATCH.format(
                            cmd=self.tabs[self.get_tab()].textbox.lint_cmd))
                subprocess.run(f'lint.bat {currdir}', shell=True)
                os.remove('lint.bat')
            else:
                with open('lint.sh', 'w') as f:
                    f.write(
                        _LINT_BATCH.format(
                            cmd=self.tabs[self.get_tab()].textbox.lint_cmd))
                subprocess.run(f'chmod 700 lint.sh && ./lint.sh {currdir}',
                               shell=True)
                os.remove('lint.sh')
            self.open_file('results.txt')
            os.remove('results.txt')
        else:
            messagebox.showerror(
                'Error', 'Linters for languages other \
            than Python is not supported (yet)')
            return

    def autopep(self):
        """Auto Pretty-Format the document"""
        currdir = self.tabs[self.get_tab()].file_dir
        subprocess.run(f'autopep8 "{currdir}" --in-place', shell=True)
        self.reload()

    def goto(self, _=None):
        if len(self.tabs) == 0:
            return
        goto_frame = ttk.Frame(self.tabs[self.get_tab()].textbox.frame)
        style = ttkthemes.ThemedStyle(goto_frame)
        style.set_theme(self.theme)
        goto_frame.pack(anchor='nw')
        ttk.Label(goto_frame,
                  text='Go to place: [Ln].[Col] ').pack(side='left')
        place = tk.Entry(goto_frame,
                         background='black',
                         foreground='white',
                         insertbackground='white',
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
