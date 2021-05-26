from src.Dialog.commondialog import InputStringDialog, YesNoDialog
from src.modules import os, tk, ttk, json, lexers
from src.tktext import EnhancedTextFrame, TextOpts
from src.highlighter import create_tags, recolorize

TESTS_FILE = ".PyPlus/Tests/tests.json"
SETTINGS_FILE = ".PyPlus/Tests/settings.json"


class TestDialog(ttk.Frame):
    def __init__(self, parent, path):
        super().__init__(parent)
        parent.forget(parent.panes()[0])
        self.pack(fill='both', expand=1)
        parent.insert('0', self)
        self.path = path = path
        self.tests_listbox = ttk.Treeview(self, show="tree")
        yscroll = ttk.Scrollbar(self, command=self.tests_listbox.yview)
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

    def refresh_tests(self):
        self.tests_listbox.delete(*self.tests_listbox.get_children())
        self.method_list = self.read_test()
        self.write_test()
        for test in self.method_list.keys():
            self.tests_listbox.insert("", "end", text=test)

    def write_test(self):
        try:
            if not os.path.isdir(os.path.join(self.path, ".PyPlus")):
                os.mkdir(os.path.join(self.path, ".PyPlus"))
            if not os.path.isdir(os.path.join(self.path, ".PyPlus", "Tests")):
                os.mkdir(os.path.join(self.path, ".PyPlus", "Tests"))
        except OSError:
            pass
        try:
            with open(os.path.join(self.path, TESTS_FILE), "w") as f:
                json.dump(self.method_list, f)
        except (AttributeError, FileNotFoundError):
            try:
                with open(os.path.join(self.path, TESTS_FILE), "w") as f:
                    json.dump({}, f)
            except FileNotFoundError:
                pass

    def read_test(self) -> dict:
        try:
            with open(os.path.join(self.path, TESTS_FILE)) as f:
                return json.load(f)
        except (ValueError, FileNotFoundError):
            return {}

    def refresh_tests(self):
        self.tests_listbox.delete(*self.tests_listbox.get_children())
        self.method_list = self.read_test()
        self.write_test()
        for test in self.method_list.keys():
            self.tests_listbox.insert("", "end", text=test)

    def write_settings(self):
        try:
            with open(os.path.join(self.path, SETTINGS_FILE), "w") as f:
                json.dump(self.settings_list, f)
        except AttributeError:
            with open(os.path.join(self.path, SETTINGS_FILE), "w") as f:
                json.dump({}, f)

    def read_settings(self) -> dict:
        try:
            with open(os.path.join(self.path, SETTINGS_FILE)) as f:
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
        TextOpts(textwidget=imports.text, bindkey=True)
        TextOpts(textwidget=setup.text, bindkey=True)
        TextOpts(textwidget=teardown.text, bindkey=True)
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
        settingswin.mainloop()

    def new(self):
        dialog = InputStringDialog(self, "New", "Name")
        name = dialog.result
        if not name:
            return
        name = "test_" + name
        codewin = tk.Toplevel(self)
        codewin.title(name)
        codewin.transient(self)
        textframe = EnhancedTextFrame(codewin)
        text = textframe.text
        text.lexer = lexers.get_lexer_by_name("Python")
        TextOpts(textwidget=text, bindkey=True)
        textframe.pack(fill="both", expand=1)
        button_frame = ttk.Frame(codewin)

        def save_and_close():
            self.modify_test(name, text.get("1.0", "end"))
            codewin.destroy()
            self.refresh_tests()

        okbtn = ttk.Button(button_frame, text="OK", command=save_and_close)
        okbtn.pack(side="left")
        cancelbtn = ttk.Button(button_frame, text="Cancel", command=codewin.destroy)
        cancelbtn.pack(side="left")
        button_frame.pack(fill="x")
        codewin.mainloop()

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
        codewin = tk.Toplevel(self)
        codewin.title(name)
        codewin.transient(self)
        textframe = EnhancedTextFrame(codewin)
        text: tk.Text = textframe.text
        text.lexer = lexers.get_lexer_by_name("Python")
        text.insert("end", self.method_list[name])
        TextOpts(text, bindkey=True)
        textframe.pack(fill="both", expand=1)
        button_frame = ttk.Frame(codewin)

        def save_and_close():
            self.modify_test(name, text.get("1.0", "end"))
            codewin.destroy()

        okbtn = ttk.Button(button_frame, text="OK", command=save_and_close)
        okbtn.pack(side="left")
        cancelbtn = ttk.Button(button_frame, text="Cancel", command=codewin.destroy)
        cancelbtn.pack(side="left")
        button_frame.pack(fill="x")
        codewin.mainloop()
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
        with open(os.path.join(self.path, "test.py"), "w") as f:
            f.write(res)
