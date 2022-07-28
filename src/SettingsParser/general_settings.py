import os
import sys
import tkinter as tk
import zipfile
from json import JSONDecodeError
from pathlib import Path
from tkinter import font

import json5 as json

from src.constants import APPDIR
from src.Dialog.commondialog import ErrorInfoDialog
from src.Dialog.filedialog import DirectoryOpenDialog, FileOpenDialog
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
        for option, value in self.get_settings("font_options").items():
            code_font[option] = value

    @staticmethod
    def zip_settings(backupdir):
        def zipdir(path, zip_obj):
            for root, _, files in os.walk(path):
                for file in files:
                    zip_obj.write(
                        os.path.join(root, file),
                        os.path.relpath(os.path.join(root, file), Path(path).parent),
                    )

        with zipfile.ZipFile(
                os.path.join(backupdir, "Config.zip"), "w", zipfile.ZIP_DEFLATED
        ) as zipobj:
            zipdir("Config/", zipobj)
        ErrorInfoDialog(title="Done", text="Settings backed up.")

    def __zipsettings(self):
        DirectoryOpenDialog(self.master, self.zip_settings)

    @staticmethod
    def unzip_settings(backupdir):
        try:
            with zipfile.ZipFile(backupdir) as zipobj:
                zipobj.extractall(path=APPDIR)
            ErrorInfoDialog(
                title="Done",
                text="Settings extracted. Please restart to apply changes.",
            )
        except (zipfile.BadZipFile, zipfile.BadZipfile, zipfile.LargeZipFile):
            pass

    def __unzipsettings(self):
        FileOpenDialog(self.master, self.unzip_settings)

    def get_settings(self, setting):
        return self.settings[setting]

    def create_menu(self, open_file, master):
        menu = tk.Menu(master)
        menu.add_command(
            label="General Settings",
            command=lambda: open_file("Config/general-settings.json"),
        )
        menu.add_command(
            label="Format Command Settings",
            command=lambda: open_file("Config/format-settings.json"),
        )
        menu.add_command(
            label="File Icon Settings",
            command=lambda: open_file("Config/file-icons.json"),
        )
        menu.add_command(
            label="Lexer Settings",
            command=lambda: open_file("Config/lexer-settings.json"),
        )
        menu.add_command(
            label="Linter Settings",
            command=lambda: open_file("Config/linter-settings.json"),
        )
        menu.add_command(
            label="Run Command Settings",
            command=lambda: open_file("Config/cmd-settings.json"),
        )
        menu.add_command(label="Backup Settings to...", command=self.__zipsettings)
        menu.add_command(
            label="Load Settings from...",
            command=lambda _: self.__unzipsettings(),
        )
        return menu
