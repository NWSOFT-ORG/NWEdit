"""Python console for the editor."""
import code
import hashlib
import io
import queue
import sys
import threading
import tkinter as tk
from tkinter import ttk

from src.Components.scrollbar import TextScrollbar
from src.Components.tktext import EnhancedText
from src.SettingsParser.general_settings import GeneralSettings
from src.Utils.functions import apply_style


# from olisolomos's gist
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

    def __init__(self, parent: tk.Misc, _locals=None, exit_callback=None):
        super().__init__(parent)
        settings_class = GeneralSettings()
        self.command_history = []
        self.font = settings_class.get_font()
        self.text = ConsoleText(
            self,
            wrap="none",
            highlightthickness=0,
            font=self.font,
            insertwidth=3,
        )
        vbar = TextScrollbar(self, command=self.text.yview, widget=self.text)
        vbar.pack(side="right", fill="y", anchor="ne")
        xbar = TextScrollbar(
            self, command=self.text.xview, orient="horizontal", widget=self.text
        )
        xbar.pack(side="bottom", fill="x", anchor="sw")
        self.text.pack(fill="both", expand=True, side="left", anchor="nw")
        self.text.config(yscrollcommand=vbar.set)
        self.text.config(xscrollcommand=xbar.set)
        self.text.insert("insert", "Python " + sys.version + "\n")

        self.shell = code.InteractiveConsole(locals=_locals)

        # make the enter key call the self.enter function
        self.text.bind("<Return>", self.enter)
        self.prompt_flag = True
        self.command_running = False
        self.exit_callback = exit_callback

        # replace all inputs and outputs
        sys.stdout = Pipe()
        sys.stderr = Pipe()
        sys.stdin = Pipe()

        self.read_from_pipe(sys.stdout, "stdout")
        self.read_from_pipe(sys.stderr, "stderr")

    def prompt(self):
        """Add a '>>> ' to the console"""
        self.prompt_flag = True

    def read_from_pipe(self, pipe: Pipe, tag_name, **kwargs):
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
        self.after(50, lambda: self.read_from_pipe(pipe, tag_name, **kwargs))

    def enter(self, _):
        """The <Return> key press handler"""

        if sys.stdin.reading:
            # if stdin requested, then put data in stdin instead of running a new command
            line = self.text.consume_last_line()
            line = line[1:] + "\n"
            sys.stdin.buffer.put(line)
            return

        # don't run multiple commands simultaneously
        if self.command_running:
            return

        # get the command text
        command = self.text.read_last_line()
        try:
            self.command_history.append(command)
            # compile it
            compiled = code.compile_command(command)
            is_complete_command = compiled is not None
        except (SyntaxError, OverflowError, ValueError):
            self.text.consume_last_line()
            self.prompt()
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


class ConsoleText(EnhancedText):
    """
    A Text widget that handles some application logic,
    e.g., having a line of input at the end with everything else being un-editable"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        apply_style(self)

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

        # keep track of where user input/commands starts, and the committed text ends
        self.committed_hash = None
        self.committed_text_backup = ""
        self.commit_all()

    def prompt(self):
        """Insert a prompt"""
        self.mark_set("prompt_end", "end-1c")
        self.mark_gravity("prompt_end", "left")
        self.write(">>> ")
        self.mark_gravity("prompt_end", "right")

    def commit_all(self):
        """Mark all texts as committed"""
        self.commit_to("end-1c")

    def commit_to(self, pos):
        """Mark all texts up to a certain position as committed"""
        if self.index(pos) in (self.index("end-1c"), self.index("end")):
            # don't let text become un-committed
            self.mark_set("committed_text", "end-1c")
            self.mark_gravity("committed_text", "left")
        else:
            # if the text is added before the last prompt (">>> "),
            # update the stored position of the tag
            for i, (tag_name, _, _) in reversed(list(enumerate(self.console_tags))):
                if tag_name == "prompt":
                    tag_ranges = self.tag_ranges("prompt")
                    self.console_tags[i] = ("prompt", tag_ranges[-2], tag_ranges[-1])
                    break

        # update the hash and backup
        self.committed_hash = self.get_committed_text_hash()
        self.committed_text_backup = self.get_committed_text()

    def get_committed_text_hash(self):
        """Get the hash of the committed area —
        used for detecting an attempt to edit it"""
        return hashlib.md5(self.get_committed_text().encode()).digest()

    def get_committed_text(self):
        """Get all text marked as committed"""
        return self.get(1.0, "committed_text")

    def write(self, string, pos="end-1c"):
        """Write some text to the console"""

        # insert the text
        self.insert(pos, string)
        self.see("end")

        # commit text
        self.commit_to(pos)

    def on_text_change(self, _):
        """If the text is changed, check if the change is part of the committed
        text, and if it is revert the change"""
        if self.get_committed_text_hash() != self.committed_hash:
            # revert change
            self.mark_gravity("committed_text", "right")
            self.replace(1.0, "committed_text", self.committed_text_backup)
            self.mark_gravity("committed_text", "left")

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
