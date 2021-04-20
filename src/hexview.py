"""A Hex Viewer to view non-text documents."""

from src.constants import BLOCK_HEIGHT, BLOCK_SIZE, BLOCK_WIDTH, ENCODINGS
from src.modules import codecs, os, tk, ttk


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

        self.frame = ttk.Frame(self.parent)
        buttonframe = ttk.Frame(self.parent)
        self.offset_label = ttk.Label(buttonframe, text="Offset")
        self.offset_spinbox = ttk.Spinbox(
            buttonframe,
            from_=0,
            textvariable=self.offset,
            increment=BLOCK_SIZE,
            foreground="black",
        )
        self.encoding_label = ttk.Label(buttonframe, text="Encoding", underline=0)
        self.encoding_combobox = ttk.Combobox(
            buttonframe, values=ENCODINGS, textvariable=self.encoding, state="readonly"
        )
        self.textbox = tk.Text(
            self.frame,
            height=BLOCK_HEIGHT,
            width=2 + (BLOCK_WIDTH * 4),
            state="disabled",
            wrap="none",
        )

        self.textbox.tag_configure("ascii", foreground="green")
        self.textbox.tag_configure("error", foreground="red")
        self.textbox.tag_configure("hexspace", foreground="navy")
        self.textbox.tag_configure("graybg", background="lightgray")
        yscroll = ttk.Scrollbar(self.frame, command=self.textbox.yview)
        self.textbox["yscrollcommand"] = yscroll.set
        buttonframe.pack(side="top")
        yscroll.pack(side="right", fill="y")
        self.offset_label.pack(side="left", anchor="nw")
        self.offset_spinbox.pack(side="left", anchor="nw")
        self.encoding_label.pack(side="left", anchor="nw")
        self.encoding_combobox.pack(side="left", anchor="nw")
        self.textbox.pack(fill="both", expand=1)
        self.frame.pack(fill="both", expand=1)

        self.parent.bind("<Alt-f>", lambda *args: self.offset_spinbox.focus())
        self.parent.bind("<Alt-e>", lambda *args: self.encoding_combobox.focus())

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
            size = os.path.getsize(filename)
            size = size - BLOCK_SIZE if size > BLOCK_SIZE else size - BLOCK_WIDTH
            self.offset_spinbox.config(to=max(size, 0))
            self.filename = filename
            self.show_block()
