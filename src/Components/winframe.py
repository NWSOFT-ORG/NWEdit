import tkinter as tk
from tkinter import font, ttk

import json5rw as json

from src.constants import OSX
from src.tktypes import Tk_Win
from src.Utils.photoimage import IconImage

RADIUS = 27 if OSX else 0


# Need these because importing settings is a circular import
def get_theme():
    with open("Config/general-settings.json") as f:
        settings = json.load(f)
        if not settings:
            return ""  # Default theme
    return settings["theme"]


def get_bg():
    style = ttk.Style()
    return style.lookup("TLabel", "background")


def get_fg():
    style = ttk.Style()
    return style.lookup("TLabel", "foreground")


def font_height():
    return font.Font(font="tkDefaultFont").metrics("linespace")


class WinFrame(tk.Toplevel):
    child_frame = None
    x = 0
    y = 0

    def __init__(
        self,
        master: Tk_Win,
        title: str,
        disable: bool = True,
        closable: bool = True,
        resizable: bool = False,
        icon: IconImage = None,
    ):
        super().__init__(master)
        self.icon = icon
        self.title_text = title
        super().title(title)  # Need a decent message to show on the taskbar
        self.update_idletasks()
        self.master = master
        self.bg = get_bg()
        if closable:
            self.bind("<Escape>", lambda _: self.destroy())
        if OSX:
            self.tk.call(
                "tk::unsupported::MacWindowStyle", "style", self._w, "floating", "closeBox"
            )
        self.wait_visibility(self)  # Fix focus issues

        if disable:
            self.grab_set()  # Linux WMs might fail to grab the window

        self.lift()
        self.bind("<Destroy>", self.on_exit)
        self._resizable = resizable

    def on_exit(self, _):
        # Release Grab to prevent issues
        self.grab_release()

    def add_widget(self, child_frame: tk.Widget):
        self.child_frame = child_frame
        self.child_frame.pack(fill="both", expand=True)
        self.child_frame.update_idletasks()

    def wm_resizable(self, width: bool = ..., height: bool = ...):
        self._resizable = bool(width or height)
        super().resizable(width, height)

    resizable = wm_resizable
