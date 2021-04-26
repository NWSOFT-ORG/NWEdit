from src.constants import APPDIR, logger
from src.modules import json, tk, ttk, ttkthemes


def get_theme():
    with open(APPDIR + "/Settings/general-settings.json") as f:
        settings = json.load(f)
    return settings["theme"]


class Dialog(tk.Toplevel):
    def __init__(self, parent: tk.Misc = None, title: str = None):
        if parent:
            super().__init__(parent)
            self.transient(parent)
        else:
            super().__init__()
            self.transient(".")

        if title:
            self.title(title)

        self.result = None
        self._style = ttkthemes.ThemedStyle()
        self._style.set_theme(get_theme())
        bg = self._style.lookup("TLabel", "background")

        self.config(background=bg)

        body = ttk.Frame(self)
        self.initial_focus = self.body(body)
        body.pack(fill="x", padx=5, pady=5)

        self.buttonbox()

        if not self.initial_focus:
            self.initial_focus = self

        self.protocol("WM_DELETE_WINDOW", self.cancel)

        self.initial_focus.focus_set()
        self.resizable(0, 0)
        self.wait_window(self)

    def body(self, master: tk.Misc):
        # create dialog body.  return widget that should have
        # initial focus.  this method should be overridden

        return master

    def buttonbox(self):
        # add standard button box. override if you don't want the
        # standard buttons

        box = ttk.Frame(self)

        w = ttk.Button(box, text="OK", width=10, command=self.ok)
        w.pack(side="left", padx=5, pady=5)
        w = ttk.Button(box, text="Cancel", width=10, command=self.cancel)
        w.pack(side="left", padx=5, pady=5)

        box.pack(fill="x")

    def ok(self, _=None):
        if not self.validate():
            self.initial_focus.focus_set()  # put focus back
            return

        self.withdraw()
        self.update_idletasks()

        self.apply()

        self.cancel()

    def cancel(self, _=None):
        self.destroy()

    @staticmethod
    def validate(_=None):
        return 1  # override

    @staticmethod
    def apply(_=None):
        pass  # override


class YesNoDialog(Dialog):
    def __init__(self, parent: tk.Misc = None, title: str = "", text: str = None):
        self.text = text
        super().__init__(parent, title)

    def body(self, master):
        label1 = ttk.Label(master, text=self.text)
        label1.pack(fill="both")

        return label1

    def buttonbox(self):
        box = ttk.Frame(self)

        b1 = ttk.Button(box, text="Yes", width=10, command=self.apply)
        b1.pack(side="left", padx=5, pady=5)
        b2 = ttk.Button(box, text="No", width=10, command=self.cancel)
        b2.pack(side="left", padx=5, pady=5)

        box.pack(fill="x")

    def apply(self, _=None):
        self.result = 1
        self.destroy()
        logger.info("apply")

    def cancel(self, _=None):
        # put focus back to the parent window
        self.result = 0
        self.destroy()
        logger.info("cancel")


class InputStringDialog(Dialog):
    def __init__(self, parent=None, title="InputString", text=""):
        self.text = text
        super().__init__(parent, title)

    def body(self, master: tk.Misc):
        label1 = ttk.Label(master, text=self.text)
        label1.pack(side="top", fill="both", expand=1)

        return label1

    def buttonbox(self):
        self.entry = ttk.Entry(self)
        self.entry.pack(fill="x", expand=1)
        box = ttk.Frame(self)

        b1 = ttk.Button(box, text="Ok", width=10, command=self.apply)
        b1.pack(side="left", padx=5, pady=5)
        b2 = ttk.Button(box, text="Cancel", width=10, command=self.cancel)
        b2.pack(side="left", padx=5, pady=5)

        box.pack(fill="x")

    def apply(self, _=None):
        self.result = self.entry.get()
        self.destroy()
        logger.info("apply")

    def cancel(self, _=None):
        # put focus back to the parent window
        self.result = 0
        self.destroy()
        logger.info("cancel")


class ErrorInfoDialog(Dialog):
    def __init__(self, parent: tk.Misc = None, text: str = None, title: str = "Error"):
        self.text = text
        super().__init__(parent, title)

    def body(self, master):
        label1 = ttk.Label(master, text=self.text)
        label1.pack(side="top", fill="both", expand=1)

        return label1

    def buttonbox(self):
        b1 = ttk.Button(self, text="Ok", width=10, command=self.apply)
        b1.pack(side="left", padx=5, pady=5)

    def apply(self, _=None):
        self.destroy()
        logger.info("apply")

    @staticmethod
    def cancel(_=None, **kwargs):
        pass


class ViewDialog(tk.Toplevel):
    def __init__(self, parent=None, title=None, text=None, file=None):
        if parent:
            super().__init__(parent)
            self.transient(parent)
            self.parent = parent
        else:
            super().__init__()
            self.transient(".")
            self.parent = None

        self.text = text
        self.file = file

        if title:
            self.title(title)

        self.result = None

        body = ttk.Frame(self)
        self.initial_focus = self.body(body)
        body.pack(fill="both", expand=1)

        self.buttonbox()

        self.grab_set()

        if not self.initial_focus:
            self.initial_focus = self

        self.protocol("WM_DELETE_WINDOW", self.cancel)

        self.work()

        self.initial_focus.focus_set()
        self.wait_window(self)

    def body(self, master):
        self.treeview = ttk.Treeview(self)
        self.treeview.pack(fill="both", expand=1)
        self.treeview.bind("<Double-1>", self.double_click)

        self.treeview.tag_configure("class", foreground="yellow")
        self.treeview.tag_configure("function", foreground="#448dc4")

    def buttonbox(self):
        box = ttk.Frame(self)

        w = ttk.Button(box, text="OK", width=10, command=self.cancel)
        w.pack(side="left")
        box.pack(fill="both", expand=1)

    def cancel(self, event=None):
        # put focus back to the parent window
        if self.parent:
            self.parent.focus_set()
        self.destroy()

    def work(self):
        filename = self.file

        self.treeview.heading("#0", text=filename)
        self.treeview.column("#0", stretch="yes", minwidth=350, width=350)
        self.i = 0

        text_lines = self.text.get("1.0", "end-1c")
        lines = text_lines.split("\n")

        self.add_nodes(lines)

    def add_nodes(self, text):
        self.find_line = {}
        x = 0
        for line in text:
            x += 1
            y = 0
            whitespaces = len(line) - len(line.lstrip())
            if line.lstrip().startswith("class"):
                node = self.treeview.insert("", "end", text=line, tags="class")
                key = "_class_" + line
                self.find_line[key] = x

                for second_line in text[x:]:
                    whitespaces_second = len(second_line) - len(second_line.lstrip())
                    y += 1
                    new_class = False
                    if not new_class:
                        if "class" in second_line:
                            l = second_line.lstrip()
                            if l.startswith("#"):
                                continue
                            new_class = True
                            key = ""
                            break
                        elif "def" in second_line:
                            l = second_line.lstrip()
                            if l.startswith("def"):
                                if l.startswith("#"):
                                    continue
                                else:
                                    if whitespaces < whitespaces_second:
                                        self.treeview.insert(
                                            node,
                                            "end",
                                            text=second_line,
                                            tags="function",
                                        )
                                        key += second_line
                                        self.find_line[key] = x + y
                                        key = "_class_" + line
                                    else:
                                        break
            elif "def" in line:
                whitespaces = len(line) - len(line.lstrip())
                if whitespaces == 0:
                    l = line.lstrip()
                    if l.startswith("def"):
                        if l.startswith("#"):
                            continue
                        else:
                            node = self.treeview.insert(
                                "", "end", text=line, tags="function"
                            )
                            key = "_root_" + line
                            self.find_line[key] = x

                    else:
                        continue

            elif "if __name__ ==" in line:
                l = line.lstrip()
                if l.startswith("if __name__"):
                    node = self.treeview.insert("", "end", line)
                    key = "_root_" + line
                    self.find_line[key] = x

    def double_click(self, event):
        item = self.treeview.identify("item", event.x, event.y)
        label = self.treeview.item(item, "text")

        if label == "":
            self.text.mark_set("insert", "1.0")
            self.text.see("insert")
            self.text.focus_force()
            return

        key = ""
        search_key = ""

        if "class" in label and "def" not in label:
            key = "_class_" + label
            z = self.find_line[key]
            self.text.mark_set("insert", "%d.0" % (z))
            self.text.see("insert")
            self.text.focus_force()

        elif "def" in label:
            child_label = label

            info = self.treeview.get_children()
            self.nodeList = []
            for i in info:
                if i.startswith("I"):
                    self.nodeList.append(i)
            parent_label = None
            for i in self.nodeList:
                if i < item:
                    parent_label = self.treeview.item(i, "text")

            if parent_label == None:
                search_key = "_root_" + child_label
                z = self.find_line[search_key]
                self.text.mark_set("insert", "%d.0" % (z))
                self.text.see("insert")
                self.text.focus_force()

            elif parent_label:
                if "class" in parent_label:
                    try:
                        search_key = "_class_" + parent_label
                        search_key += child_label
                        z = self.find_line[search_key]
                        self.text.mark_set("insert", "%d.0" % (z))
                        self.text.see("insert")
                        self.text.focus_force()
                    except:
                        # exception class ends -> change to def in _root_
                        search_key = "_root_" + child_label
                        z = self.find_line[search_key]
                        self.text.mark_set("insert", "%d.0" % (z))
                        self.text.see("insert")
                        self.text.focus_force()

                else:
                    search_key = "_root_" + child_label
                    z = self.find_line[search_key]
                    self.text.mark_set("insert", "%d.0" % (z))
                    self.text.see("insert")
                    self.text.focus_force()

        elif "if __name__" in label:
            key = "_root_" + label
            z = self.find_line[key]
            self.text.mark_set("insert", "%d.0" % (z))
            self.text.see("insert")
            self.text.focus_force()
