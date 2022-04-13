from src.Dialog.search import re_search
from src.modules import os, threading, tk, ttk
from src.Widgets.tkentry import Entry


def list_all(directory: str) -> list:
    itemslist = os.listdir(directory)
    files = []
    for file in itemslist:
        path = os.path.abspath(os.path.join(directory, file))
        if os.path.isdir(path):
            files += list_all(path)
        else:
            files.append(path)
    files.sort()
    return files


class SearchInDir(ttk.Frame):
    def __init__(self, parent: ttk.Notebook, path: str, opencommand: callable):
        super().__init__(parent)
        self.pack(fill="both", expand=1)
        parent.add(self, text="Search in Directory")

        self.parent = parent
        self.path = path
        self.opencommand = opencommand

        # Tkinter Variables
        self.case = tk.BooleanVar()
        self.regex = tk.BooleanVar()
        self.fullword = tk.BooleanVar()

        self.found = {}
        ttk.Label(self, text="Search: ").pack(side="top", anchor="nw", fill="y")
        self.content = Entry(self)
        self.content.pack(side="top", fill="both")
        ttk.Button(
            self,
            text="Search",
            takefocus=False,
            command=lambda: threading.Thread(target=self.find).start(),
        ).pack(side="top", fill="x")

        progressbar_frame = ttk.Frame(self)
        self.search_stat = ttk.Label(
            progressbar_frame, text="Press 'Search' to start searching."
        )
        self.search_stat.pack(fill="x")
        self.progressbar = ttk.Progressbar(progressbar_frame)
        self.progressbar.pack(side="top", fill="x")
        progressbar_frame.pack(side="top", fill="both")
        # Checkboxes
        checkbox_frame = ttk.Frame(self)
        self.case_yn = ttk.Checkbutton(
            checkbox_frame, text="Case Sensitive", variable=self.case
        )
        self.case_yn.pack(side="left")

        self.reg_yn = ttk.Checkbutton(
            checkbox_frame, text="RegExp", variable=self.regex
        )
        self.reg_yn.pack(side="left")

        self.fullw_yn = ttk.Checkbutton(
            checkbox_frame, text="Full Word", variable=self.fullword
        )
        self.fullw_yn.pack(side="left")

        checkbox_frame.pack(side="top", fill="both")

        treeframe = ttk.Frame(self)
        self.tree = ttk.Treeview(treeframe, show="tree")
        self.tree.pack(side="left", fill="both", expand=1)

        yscroll = ttk.Scrollbar(treeframe, command=self.tree.yview)
        yscroll.pack(side="right", fill="y")
        self.tree.config(yscrollcommand=yscroll.set)
        self.tree.bind("<Double-1>", self.on_double_click)
        treeframe.pack(fill="both", expand=1)

        for x in (self.case, self.regex, self.fullword):
            x.trace_add("write", self.find)

        self.content.insert("end", "e")

    def find(self, *_):
        path = self.path
        files = list_all(path)
        self.found.clear()
        s = self.content.get()

        self.progressbar["value"] = 0
        self.progressbar["maximum"] = len(files)

        if s:
            for file in files:
                new_status = self.progressbar["value"] + 1
                self.progressbar["value"] = new_status
                self.search_stat.config(
                    text=f"Searching in file {new_status}/{len(files)}"
                )
                try:
                    with open(file, "rb") as f:
                        matches = re_search(
                            s,
                            f.read().decode("utf-8"),
                            nocase=not (self.case.get()),
                            regex=self.regex.get(),
                        )
                except (UnicodeDecodeError, PermissionError):
                    continue
                if not matches:
                    continue
                self.found[file] = [
                    (f"{x[0][0]}.{x[0][1]}", f"{x[1][0]}.{x[1][1]}") for x in matches
                ]
            self.search_stat.config(text="Search Completed!")
            self.update_treeview()

    def update_treeview(self):
        self.search_stat.config(text="Updating results...")
        self.tree.delete(*self.tree.get_children())
        found_list = self.found.keys()
        for k in found_list:
            parent = self.tree.insert("", "end", text=k, open=True)
            for pos in self.found[k]:
                pos = pos[0]
                self.tree.insert(parent, "end", text=f"Line {pos}")
        self.search_stat.config(text="Finished! Press Search to search again.")

    def on_double_click(self, event: tk.Event = None):
        try:
            item = self.tree.identify("item", event.x, event.y)
            text = self.tree.item(item, "text")

            if os.path.isfile(text):
                self.opencommand(text)
            else:
                parent = self.tree.parent(item)
                parenttext = self.tree.item(parent, "text")
                textbox = self.opencommand(parenttext)
                ls = text.split()
                start = ls[0]
                end = ls[-1]
                textbox.tag_remove("sel", "1.0", "end")
                textbox.tag_add("sel", start, end)
                textbox.mark_set("insert", start)
                textbox.see("insert")
        except tk.TclError:
            pass
