import sys
import tkinter as tk
from tkinter import ttk
from typing import *

import json5 as json
from pygments import styles

from src.types import Tk_Win
from src.Utils.images import get_image
from src.Widgets.tktext import EnhancedTextFrame
from src.Widgets.winframe import WinFrame


# Need these to prevent circular imports
def get_pygments() -> Text:
    with open("Config/general-settings.json") as f:
        settings = json.load(f)
    return settings["pygments"]


def get_font() -> Text:
    with open("Config/general-settings.json") as f:
        settings = json.load(f)
    return settings["font"]


class ReadonlyText(EnhancedTextFrame):
    def __init__(self, master: Union[Literal["."], tk.Misc]) -> None:
        super().__init__(master)
        style = styles.get_style_by_name(get_pygments())
        bgcolor = style.background_color
        fgcolor = "#f00"
        self.text.configure(state="disabled", fg=fgcolor, bg=bgcolor, font=get_font())

    def insert(self, pos: Text, text: Text) -> None:
        self.text.configure(state="normal")
        self.text.insert(pos, text)
        self.text.configure(state="disabled")

    def delete(self, pos1: Text, pos2: Text) -> None:
        self.text.configure(state="normal")
        self.text.delete(pos1, pos2)
        self.text.configure(state="disabled")


class ErrorReportDialog(WinFrame):
    def __init__(self, master: Tk_Win, error_name: Text, error_message: Text) -> None:
        super().__init__(master, error_name, closable=False, icon=get_image("error"))
        master.withdraw()
        ttk.Label(self, text="Please consider reporting a bug on github.").pack(
            anchor="nw", fill="x"
        )
        text = ReadonlyText(self)
        text.insert("end", error_message)
        text.pack(fill="both")

        self.protocol("WM_DELETE_WINDOW", lambda: sys.exit(1))


class LogViewDialog(WinFrame):
    def __init__(self, master: Tk_Win) -> None:
        super().__init__(master, "PyPlus Log", icon=get_image("info"))
        self.title("Log view")
        frame = ttk.Frame(self)
        frame.pack(anchor="nw", fill="x")
        ttk.Label(frame, text="Debug log").pack(anchor="nw", side="left")
        ttk.Button(frame, text="Copy", command=self.copy_log, takefocus=False).pack(
            side="right"
        )
        self.log_text = ReadonlyText(self)
        self.log_text.pack(fill="both", expand=1)
        self.log_text.after(10, self.update_log)

    def update_log(self) -> None:
        with open("pyplus.log") as f:
            log = f.read()
        self.log_text.delete("1.0", "end")
        self.log_text.insert("end", log)
        self.log_text.text.see("end")
        self.log_text.after(10, self.update_log)

    def copy_log(self) -> None:
        self.log_text.clipboard_clear()
        self.log_text.clipboard_append(self.log_text.get("1.0", "end"))
