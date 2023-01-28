import tkinter as tk
from pathlib import Path
from tkinter import ttk

import json5rw as json

from src.Components.codeinputdialog import CodeInputDialog
from src.Components.commondialog import StringInputDialog, YesNoDialog
from src.Components.scrollbar import Scrollbar
from src.Components.tktext import EnhancedTextFrame, TextOpts
from src.constants import APPDIR
from src.SettingsParser.configfiles import config_dir_from_name, SETTINGS_FILE, TESTS_FILE
from src.SettingsParser.extension_settings import RunCommand
from src.Utils.functions import is_valid_name, shell_command


class TestDialog(ttk.Frame):
    def __init__(self, master: ttk.Notebook, path: Path):
        self.master = master
        super().__init__(master)
        self.pack(fill="both", expand=1)
        master.add(self, text="Unit testing")
        self.path: Path = path
        self.tests_listbox = ttk.Treeview(self, show="tree")
        yscroll = Scrollbar(self, command=self.tests_listbox.yview)
        yscroll.pack(side="right", fill="y")
        self.tests_listbox.config(yscrollcommand=yscroll.set)
        self.refresh_tests()
        self.settings_list = self.read_settings()
        self.tests_listbox.pack(fill="both", expand=1)
        self.button_frame = ttk.Frame(self)
        ttk.Button(self.button_frame, text="New", command=self.new).pack(side="left")
        ttk.Button(self.button_frame, text="Delete", command=self.delete).pack(
            side="left"
        )
        ttk.Button(self.button_frame, text="Edit", command=self.edit).pack(side="left")
        ttk.Button(self.button_frame, text="Run All Tests", command=self.run_test).pack(
            side="left"
        )
        ttk.Button(self.button_frame, text="...", command=self.settings).pack(
            side="left"
        )
        self.button_frame.pack(side="bottom")

        self.cmd_settings_class = RunCommand()

    def refresh_tests(self):
        self.tests_listbox.delete(*self.tests_listbox.get_children())
        self.method_list = self.read_test()
        self.write_test()
        for test in self.method_list.keys():
            self.tests_listbox.insert("", "end", text=test)

    def write_test(self):
        try:
            config_dir = config_dir_from_name(self.path)
            if not config_dir.is_dir():
                config_dir.mkdir()
            tests_dir = config_dir / "Tests"
            if not tests_dir.is_dir():
                tests_dir.mkdir()
        except OSError:
            pass
        try:
            with Path(self.path, TESTS_FILE).open("w") as f:
                json.dump(self.method_list, f)
        except (AttributeError, FileNotFoundError):
            try:
                with Path(self.path, TESTS_FILE).open("w") as f:
                    json.dump({}, f)
            except FileNotFoundError:
                pass

    def read_test(self) -> dict:
        try:
            with (self.path / TESTS_FILE).open() as f:
                return json.load(f)
        except (ValueError, FileNotFoundError):
            return {}

    def write_settings(self):
        settings_file = self.path / SETTINGS_FILE
        with settings_file.open("w") as f:
            json.dump(self.settings_list, f)

    def read_settings(self) -> dict:
        settings_file = self.path / SETTINGS_FILE
        try:
            with settings_file.open() as f:
                return json.load(f)
        except (ValueError, FileNotFoundError):
            return {"imports": "", "setup": "", "teardown": ""}

    def modify_test(self, name, code):
        self.method_list[name] = code
        self.write_test()

    def modify_settings(self, setting_name, setting):
        self.settings_list[setting_name] = setting
        self.write_settings()

    def settings(self):
        settingswin = tk.Toplevel(self)
        settingswin.title("Modify Settings")
        settingswin.geometry("500x400")
        imports = EnhancedTextFrame(settingswin)
        setup = EnhancedTextFrame(settingswin)
        teardown = EnhancedTextFrame(settingswin)
        TextOpts(settingswin, bindkey=True).set_text(imports.text)
        TextOpts(settingswin, bindkey=True).set_text(setup.text)
        TextOpts(settingswin, bindkey=True).set_text(teardown.text)
        imports.text["height"] = 3
        setup.text["height"] = 3
        teardown.text["height"] = 3
        ttk.Label(settingswin, text="Imports").pack(fill="both", expand=1)
        imports.pack(fill="both", expand=1)
        imports.text.insert("end", self.settings_list["imports"])
        ttk.Label(settingswin, text="SetUp").pack(fill="both", expand=1)
        setup.pack(fill="both", expand=1)
        setup.text.insert("end", self.settings_list["setup"])
        ttk.Label(settingswin, text="TearDown").pack(fill="both", expand=1)
        teardown.pack(fill="both", expand=1)
        teardown.text.insert("end", self.settings_list["teardown"])

        def save_and_close():
            self.modify_settings("imports", imports.text.get("1.0", "end"))
            self.modify_settings("setup", setup.text.get("1.0", "end"))
            self.modify_settings("teardown", teardown.text.get("1.0", "end"))
            self.write_settings()
            settingswin.destroy()

        ttk.Button(settingswin, text="OK", command=save_and_close).pack(fill="both")

    def new(self):
        dialog = StringInputDialog(self, "New", "Name")
        name = dialog.result
        if not name:
            return
        name = "test_" + name
        if not is_valid_name(name):
            return
        win = CodeInputDialog(self, name, lambda: self.modify_test(name, win.text.get("1.0", "end")))
        self.refresh_tests()

    def delete(self):
        sel = self.tests_listbox.item(self.tests_listbox.focus(), "text")
        if not sel:
            return
        if YesNoDialog(self, title="Confirm", text="Are you sure?").result:
            del self.method_list[sel]
            self.write_test()
            self.refresh_tests()

    def edit(self):
        name = self.tests_listbox.item(self.tests_listbox.focus(), "text")
        if not name:
            return
        win = CodeInputDialog(self, f"Editing {name}", lambda: self.modify_test(name, win.text.get("1.0", "end")))
        win.text.insert("end", self.method_list[name])

        self.refresh_tests()

    def run_test(self):
        modules = self.settings_list["imports"]
        teardown = self.settings_list["teardown"]
        setup = self.settings_list["setup"]
        method_list = self.method_list
        method_list["setUp"] = setup
        method_list["tearDown"] = teardown
        res = f"""import unittest
{modules}

class TestMain(unittest.TestCase):
"""
        for key, value in method_list.items():
            values = ""
            for line in value.splitlines():
                values += " " * 8 + line + "\n"
            res += f"""
    def {key}():
{values}
"""
        res += """
if __name__ == '__main__':
    unittest.main()"""
        with (self.path / "test.py").open("w") as f:
            f.write(res)
            filename = f.name

        cmd = self.cmd_settings_class.get_settings("py")
        shell_command(f"{cmd} {filename} && exit", cwd=APPDIR)
