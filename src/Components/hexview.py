"""A Hex Viewer to view non-text documents."""

import codecs
import os
import tkinter as tk
from tkinter import ttk

from src.Components.scrollbar import TextScrollbar
from src.constants import BLOCK_HEIGHT, BLOCK_WIDTH, ENCODINGS
from src.tktypes import Tk_Widget
from src.Utils.functions import apply_style


class HexView:
    """
    Copyright © 2016-20 Qtrac Ltd. All rights reserved.
    This program or module is free software: you can redistribute it and/or
    modify it under the terms of the GNU General Public License as published
    by the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version. It is provided for educational
    purposes and is distributed in the hope that it will be useful, but
    WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
    General Public License for more details."""

    def __init__(self, master: Tk_Widget):
        """Initializes the class"""
        self.master = master
        self.filename = None
        self.offset = tk.IntVar()
        self.offset.set(0)
        self.encoding = tk.StringVar()
        self.encoding.set(ENCODINGS[0])

        buttonframe = ttk.Frame(self.master)
        self._style = ttk.Style(self.master)
        self.encoding_label = ttk.Label(buttonframe, text="Encoding")
        self.encoding_combobox = ttk.Combobox(
            buttonframe, values=ENCODINGS, textvariable=self.encoding, state="readonly"
        )
        buttonframe.pack(fill="x")

        self.textbox = tk.Text(self.master)
        apply_style(self.textbox)
        self.textbox.config(
            height=BLOCK_HEIGHT,
            width=2 + (BLOCK_WIDTH * 4),
            state="disabled",
        )

        xscroll = TextScrollbar(self.master, command=self.textbox.xview, widget=self.textbox, orient="horizontal")
        xscroll.pack(side="bottom", fill="x", anchor="nw")
        yscroll = TextScrollbar(self.master, command=self.textbox.yview, widget=self.textbox)
        yscroll.pack(side="right", fill="y")
        self.textbox["yscrollcommand"] = yscroll.set
        self.textbox["xscrollcommand"] = xscroll.set

        self.textbox.tag_configure("ascii", foreground="green")
        self.textbox.tag_configure("error", foreground="red")
        self.textbox.tag_configure("hexspace", foreground="navy")
        self.textbox.tag_configure("graybg", background="lightgray")
        self.encoding_label.pack(side="left", anchor="nw")
        self.encoding_combobox.pack(side="left", anchor="nw")
        self.textbox.pack(fill="both", expand=1)
        self.encoding.trace_variable("w", self.show_block)

        self.textbox.bind("<B1-Motion>", "break")

    def show_bytes(self, row):
        self.textbox.config(state="normal")
        for byte in row:
            tags = ()
            if byte in b"\t\n\r\v\f":
                tags = ("hexspace", "graybg")
            elif 0x20 < byte < 0x7F:
                tags = ("ascii",)
            self.textbox.insert("end", "{:02X}".format(byte), tags)
            self.textbox.insert("end", " ")
        if len(row) < BLOCK_WIDTH:
            self.textbox.insert("end", " " * (BLOCK_WIDTH - len(row)) * 3)
        self.textbox.config(state="disabled")

    def show_line(self, row):
        self.textbox.config(state="normal")
        for char in codecs.decode(row, self.encoding.get().upper(), errors="replace"):
            tags = ()
            if char in "\u2028\u2029\t\n\r\v\f\uFFFD":
                char = "."
                tags = ("graybg" if char == "\uFFFD" else "error",)
            elif 0x20 < ord(char) < 0x7F:
                tags = ("ascii",)
            elif not 0x20 <= ord(char) <= 0xFFFF:  # Tcl/Tk limit
                char = "\uFFFD"
                tags = ("error",)
            self.textbox.insert("end", char, tags)
        self.textbox.insert("end", "\n")
        self.textbox.config(state="disabled")

    def open(self, filename):
        if filename and os.path.isfile(filename):
            self.filename = filename
            self.show_block()

    def show_block(self, *_):
        self.textbox.config(state="normal")
        self.textbox.delete("1.0", "end")
        if not self.filename:
            return
        with open(self.filename, "rb") as file:
            block = file.read()
        rows = [block[i: i + BLOCK_WIDTH] for i in range(0, len(block), BLOCK_WIDTH)]
        for row in rows:
            self.show_bytes(row)
            self.show_line(row)
        self.textbox.insert("end", "\n")
        self.textbox.config(state="disabled")
