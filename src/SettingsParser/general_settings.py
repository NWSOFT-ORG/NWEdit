from tkinter import font

import json5rw as json

from src.tktypes import Tk_Widget
from src.window import get_window


class GeneralSettings:
    """A class to read data to/from general-settings.json"""

    def __init__(self, master: Tk_Widget = None):
        if master is None:
            master = get_window()
        self.master = master
        with open("Config/default/general-settings.json") as f:
            self.settings = json.load(f)
        with open("Config/general-settings.json") as f:
            self.settings |= json.load(f)

    def get_font(self):
        code_font = font.Font(
            family=self.get_settings("font"),
            size=self.get_settings("font_size")
        )
        font_options = self.get_settings("font_options")
        if not font_options:
            return code_font
        for option, value in font_options.items():
            code_font[option] = value
        return code_font

    def get_settings(self, setting):
        if self.settings:
            return self.settings[setting]
