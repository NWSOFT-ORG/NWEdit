import subprocess

from src.Dialog.commondialog import InputStringDialog, YesNoDialog
from src.modules import os, tk, ttk, json, lexers
from src.Widgets.tktext import EnhancedTextFrame, TextEditingPlugin
from src.functions import is_valid_name
from src.constants import APPDIR
from src.settings import RunCommand

TESTS_FILE = ".PyPlus/Tests/tests.json"
SETTINGS_FILE = ".PyPlus/Tests/settings.json"


def create_buttonframe(button_frame: ttk.Frame, save_and_close: callable, codewin: tk.Toplevel):
    okbtn = ttk.Button(button_frame, text="OK", command=save_and_close)
    okbtn.pack(side="left")
    cancelbtn = ttk.Button(button_frame, text="Cancel", command=codewin.destroy)
    cancelbtn.pack(side="left")
    button_frame.pack(fill="x")


# noinspection PyTypeChecker
class TestDialog(ttk.Frame):
    def __init__(self, parent: [tk.Tk, tk.Misc], path: str) -> None:
        super().__init__(parent)
        self.pack(fill='both', expand=True)
        parent.add(self, text="Unit Testing")
        self.path = path
        self.tests_listbox = ttk.Treeview(self, show="tree")
        yscroll = ttk.Scrollbar(self, command=self.tests_listbox.yview)
        yscroll.pack(side="right", fill="y")
        self.tests_listbox.config(yscrollcommand=yscroll.set)
        self.refresh_tests()
        self.settings_list = self.read_settings()
        self.tests_listbox.pack(fill="both", expand=True)
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
        self.button_frame.pack(side="bottom", anchor="nw")
        
        self.cmd_settings_class = RunCommand()

    def refresh_tests(self) -> None:
        try:
            self.tests_listbox.delete(*self.tests_listbox.get_children())
            self.method_list = self.read_test()
            self.write_test()
            for test in self.method_list.keys():
                self.tests_listbox.insert("", "end", text=test)
        except tk.TclError:
            pass

    def write_test(self) -> None:
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

    def write_settings(self) -> None:
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
            return {"imports": "pass", "setup": "pass", "teardown": "pass"}

    def modify_test(self, name: str, code: str) -> None:
        self.method_list[name] = code
        self.write_test()

    def modify_settings(self, setting_name: str, setting: str) -> None:
        """Modify key-value settings"""
        self.settings_list[setting_name] = setting
        self.write_settings()

    def settings(self) -> None:
        settingswin = tk.Toplevel(self)
        settingswin.title("Modify Settings")
        settingswin.geometry("500x400")
        imports = EnhancedTextFrame(settingswin)
        setup = EnhancedTextFrame(settingswin)
        teardown = EnhancedTextFrame(settingswin)
        TextEditingPlugin(bindkey=True).set_text(imports.text)
        TextEditingPlugin(bindkey=True).set_text(setup.text)
        TextEditingPlugin(bindkey=True).set_text(teardown.text)
        imports.text["height"] = 3
        setup.text["height"] = 3
        teardown.text["height"] = 3
        ttk.Label(settingswin, text="Imports").pack(fill="both", expand=True)
        imports.pack(fill="both", expand=True)
        imports.text.insert("end", self.settings_list["imports"])
        ttk.Label(settingswin, text="SetUp").pack(fill="both", expand=True)
        setup.pack(fill="both", expand=True)
        setup.text.insert("end", self.settings_list["setup"])
        ttk.Label(settingswin, text="TearDown").pack(fill="both", expand=True)
        teardown.pack(fill="both", expand=True)
        teardown.text.insert("end", self.settings_list["teardown"])

        def save_and_close():
            self.modify_settings("imports", imports.text.get("1.0", "end"))
            self.modify_settings("setup", setup.text.get("1.0", "end"))
            self.modify_settings("teardown", teardown.text.get("1.0", "end"))
            self.write_settings()
            settingswin.destroy()

        ttk.Button(settingswin, text="OK", command=save_and_close).pack(fill="both")
        settingswin.mainloop()

    def new(self) -> None:
        dialog = InputStringDialog(self.master, "New", "Name")
        name = dialog.result
        if not name:
            return
        name = "test_" + name
        if not is_valid_name(name):
            return
        codewin = tk.Toplevel(self)
        codewin.title(name)
        codewin.transient(self.master)
        textframe = EnhancedTextFrame(codewin)
        text = textframe.text
        text.insert('end', 'pass')
        text.lexer = lexers.get_lexer_by_name("Python")
        TextEditingPlugin(bindkey=True).set_text(text)
        textframe.pack(fill="both", expand=True)
        button_frame = ttk.Frame(codewin)

        def save_and_close():
            self.modify_test(name, text.get("1.0", "end"))
            codewin.destroy()
            self.refresh_tests()

        create_buttonframe(button_frame, save_and_close, codewin)
        codewin.mainloop()

    def delete(self) -> None:
        sel = self.tests_listbox.item(self.tests_listbox.focus(), "text")
        if not sel:
            return
        if YesNoDialog(self.master, title="Confirm", text="Are you sure?").result:
            del self.method_list[sel]
            self.write_test()
            self.refresh_tests()

    def edit(self) -> None:
        name = self.tests_listbox.item(self.tests_listbox.focus(), "text")
        if not name:
            return
        codewin = tk.Toplevel(self)
        codewin.title(name)
        codewin.transient(self.master)
        textframe = EnhancedTextFrame(codewin)
        text: tk.Text = textframe.text
        text.lexer = lexers.get_lexer_by_name("Python")
        text.insert("end", self.method_list[name])
        TextEditingPlugin(bindkey=True).set_text(text)
        textframe.pack(fill="both", expand=True)
        button_frame = ttk.Frame(codewin)

        def save_and_close():
            self.modify_test(name, text.get("1.0", "end"))
            codewin.destroy()

        create_buttonframe(button_frame, save_and_close, codewin)
        codewin.mainloop()
        self.refresh_tests()

    def run_test(self) -> None:
        """Write formatted test program to the file"""
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
        res += '''
if __name__ == '__main__':
    unittest.main()'''
        with open(os.path.join(self.path, "test.py"), "w") as f:
            f.write(res)
            filename = f.name
            
        cmd = self.cmd_settings_class.get_settings('py')
        subprocess.call(f"{cmd} {filename} && exit", cwd=APPDIR)
