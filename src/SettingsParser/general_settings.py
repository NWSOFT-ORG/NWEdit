import sys
from json import JSONDecodeError
from tkinter import font

import json5 as json

from src.Components.commondialog import ErrorInfoDialog
from src.types import Tk_Widget


class GeneralSettings:
    """A class to read data to/from general-settings.json"""

    def __init__(self, master: Tk_Widget = "."):
        self.master = master
        try:
            with open("Config/general-settings.json") as f:
                self.settings = json.load(f)

        except JSONDecodeError:
            ErrorInfoDialog(self.master, text="Setings are corrupted.")
            sys.exit(1)

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

    def get_settings(self, setting):
        if self.settings:
            return self.settings[setting]
