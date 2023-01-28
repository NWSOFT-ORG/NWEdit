import tkinter as tk
from pathlib import Path
from tkinter import ttk
from typing import Dict, List

import json5rw as json

from src.Components.tkentry import Entry
from src.Components.winframe import WinFrame
from src.SettingsParser.configfiles import DEFAULT_FILE_EXTENS, FILE_EXTENS
from src.tktypes import Tk_Widget
from src.Utils.functions import is_illegal_filename
from src.Utils.images import get_image


class NewItemDialog(WinFrame):
    def __init__(self, treeview, master: Tk_Widget, opencommand):
        super().__init__(master, "New Item", icon=get_image("new"))
        with DEFAULT_FILE_EXTENS.open() as f:
            self.config: Dict[str, List[str]] = json.load(f)
        with FILE_EXTENS.open() as f:
            self.config |= json.load(f)

        frame = ttk.Frame(self)

        self.extension_tree = ttk.Treeview(frame, show="tree", selectmode="browse")
        self.extension_tree.pack(side="left", fill="both")
        self.extension_tree.bind("<<TreeviewSelect>>", self.select)
        self.make_treeview()

        self.filetree = treeview
        self.opencommand = opencommand

        self.extens_var = tk.StringVar()

        self.right_frame = ttk.Frame(frame)
        self.right_frame.pack(side="right", fill="both")

        ttk.Label(self.right_frame, text="Name: ").grid(row=0, column=0)
        self.name = Entry(self.right_frame)
        self.name.grid(row=0, column=1, sticky="ew")
        self.name.entry.bind("<KeyRelease>", self.on_name_change)
        self.name_status = ttk.Label(self.right_frame, foreground="red")
        self.name_status.grid(row=0, column=2, sticky="e")

        ttk.Label(self.right_frame, text="Extension: ").grid(row=1, column=0)
        self.extens = ttk.Combobox(self.right_frame, textvariable=self.extens_var)
        self.extens.grid(row=1, column=1, sticky="ew")
        self.extension_status = ttk.Label(self.right_frame, foreground="red")
        self.extension_status.grid(row=1, column=2)

        self.create_btn = ttk.Button(
            self.right_frame, text="Create",
            command=lambda: self.create_file(
                f"{self.name.get()}{'.' if self.extens.get() else ''}{self.extens.get()}"
            )
        )
        self.create_btn.grid(row=2, column=2, sticky="e")

        self.extens_var.trace_add("write", self.on_extens_change)

        self.add_widget(frame)
        self.update_idletasks()
        self.resizable(False, False)

    def create_file(self, file_name):
        tree: ttk.Treeview = self.filetree.tree
        directory = self.filetree.get_path(tree.focus(), append_name=True, expect_type="dir")
        path = Path(directory, file_name)
        with path.open("w") as f:
            f.write("")
        self.opencommand(path)

        self.destroy()
        self.filetree.refresh_tree()

    def on_extens_change(self, *_):
        extens = self.extens.get()

        if len(extens) > 5:  # When the extension is not recommended
            self.extension_status["text"] = "This extension is too long"
        if is_illegal_filename(extens):  # When it is illegal, should return early
            self.extension_status["text"] = "Invalid extension"
            self.create_btn["state"] = "disabled"
            return

        self.create_btn["state"] = "normal"
        self.extension_status["text"] = ""

    # noinspection DuplicatedCode
    def on_name_change(self, _):
        name = self.name.get()

        if is_illegal_filename(name) is None:  # When the name is not recommended
            self.name_status["text"] = "This filename is legal, though not recommended. It is considered too long"
        if is_illegal_filename(name):  # When it is illegal, should return early
            self.name_status["text"] = "Invalid filename"
            self.create_btn["state"] = "disabled"
            return

        self.create_btn["state"] = "normal"
        self.name_status["text"] = ""

    def select(self, _):
        item = self.extension_tree.focus()
        text = self.extension_tree.item(item, "text")

        vals = self.config[text]
        self.extens.config(values=vals)

    def make_treeview(self):
        for key in self.config.keys():
            self.extension_tree.insert("", "end", text=key)
