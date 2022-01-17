"""A Hex Viewer to view non-text documents."""

from src.constants import BLOCK_HEIGHT, BLOCK_WIDTH, ENCODINGS
from src.Dialog.commondialog import get_theme
from src.modules import codecs, os, tk, ttk, ttkthemes
from src.Widgets.tktext import EnhancedTextFrame


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

    def __init__(self, parent):
        """Initializes the class"""
        self.parent = parent
        self.filename = None
        self.offset = tk.IntVar()
        self.offset.set(0)
        self.encoding = tk.StringVar()
        self.encoding.set(ENCODINGS[0])

        buttonframe = ttk.Frame(self.parent)
        self._style = ttkthemes.ThemedStyle()
        self._style.set_theme(get_theme())
        self.encoding_label = ttk.Label(buttonframe, text="Encoding")
        self.encoding_combobox = ttk.Combobox(
            buttonframe, values=ENCODINGS, textvariable=self.encoding, state="readonly"
        )
        textframe = EnhancedTextFrame(self.parent)
        self.textbox = textframe.text
        self.textbox.config(
            height=BLOCK_HEIGHT,
            width=2 + (BLOCK_WIDTH * 4),
            state="disabled",
        )

        self.textbox.tag_configure("ascii", foreground="green")
        self.textbox.tag_configure("error", foreground="red")
        self.textbox.tag_configure("hexspace", foreground="navy")
        self.textbox.tag_configure("graybg", background="lightgray")
        self.encoding_label.pack(side="left", anchor="nw")
        self.encoding_combobox.pack(side="left", anchor="nw")
        textframe.pack(fill="both", expand=1)
        self.encoding.trace_variable("w", self.show_block)

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
        if filename and os.path.exists(filename):
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
