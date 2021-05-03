from src.dialogs import InputStringDialog, YesNoDialog
from src.modules import os, tk, ttk, json, lexers
from src.tktext import EnhancedTextFrame
from src.highlighter import create_tags, recolorize


class TestDialog(tk.Toplevel):
    def __init__(self, parent, path):
        if parent:
            super().__init__(parent)
            self.transient(parent)
        self.path = path = path

        self.title("Unit Tests")
        self.resizable(0, 0)
        self.tests_listbox = ttk.Treeview(self, show="tree")
        yscroll = ttk.Scrollbar(self, command=self.tests_listbox.yview)
        yscroll.pack(side="right", fill="y")
        self.tests_listbox.config(yscrollcommand=yscroll.set)
        self.refresh_tests()
        self.tests_listbox.pack(fill="both")
        self.button_frame = ttk.Frame(self)
        ttk.Button(self.button_frame, text="New", command=self.new).pack(side="left")
        ttk.Button(self.button_frame, text="Delete", command=self.delete).pack(
            side="left"
        )
        ttk.Button(self.button_frame, text="Edit", command=self.edit).pack(side="left")
        ttk.Button(self.button_frame, text="Run All Tests", command=self.run_test).pack(side="left")
        self.button_frame.pack(side="bottom")
        self.mainloop()

    def refresh_tests(self):
        self.tests_listbox.delete(*self.tests_listbox.get_children())
        self.method_list = self.read_test()
        self.write_test()
        for test in self.method_list.keys():
            self.tests_listbox.insert("", "end", text=test)

    def write_test(self):
        if not os.path.isfile((os.path.join(self.path, ".PyPlus/tests.json"))):
            os.mkdir((os.path.join(self.path, ".PyPlus")))
        try:
            with open(os.path.join(self.path, ".PyPlus/tests.json"), "w") as f:
                json.dump(self.method_list, f)
        except AttributeError:
            with open(os.path.join(self.path, ".PyPlus/tests.json"), "w") as f:
                json.dump({}, f)

    def read_test(self) -> dict:
        try:
            with open(os.path.join(self.path, ".PyPlus/tests.json")) as f:
                return json.load(f)
        except (ValueError, FileNotFoundError):
            return {}

    def modify_test(self, name, code):
        self.method_list[name] = code
        self.write_test()

    def new(self):
        dialog = InputStringDialog(self.master, "New", "Name")
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
        create_tags(text)
        recolorize(text)
        text.bind("<KeyRelease>", lambda _=None: recolorize(text))
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
        create_tags(text)
        recolorize(text)
        text.bind("<KeyRelease>", lambda _=None: recolorize(text))
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
        res = '''import unittest

class TestMain(unittest.TestCase):'''
        for key, value in self.method_list.items():
            values = ''
            for line in value.splitlines():
                values += '        ' + line + '\n'
            res += f'''
    def {key}():
{values}
'''
        with open(os.path.join(self.path, 'test.py'), 'w') as f:
            f.write(res)
