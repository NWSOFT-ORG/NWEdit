"""A Hex Viewer to view non-text documents."""

from constants import *


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
General Public License for more details.
"""

    def __init__(self, parent):
        """Initializes the class"""
        self.parent = parent
        self.filename = None
        self.offset = tk.IntVar()
        self.offset.set(0)
        self.encoding = tk.StringVar()
        self.encoding.set(ENCODINGS[0])

        frame = self.frame = ttk.Frame(self.parent)
        self.offset_label = ttk.Label(frame, text="Offset")
        self.offset_spinbox = ttk.Spinbox(frame,
                                          from_=0,
                                          textvariable=self.offset,
                                          increment=BLOCK_SIZE,
                                          foreground='black')
        self.encoding_label = ttk.Label(frame, text="Encoding", underline=0)
        self.encoding_combobox = ttk.Combobox(frame,
                                              values=ENCODINGS,
                                              textvariable=self.encoding,
                                              state="readonly")
        self.textbox = tk.Text(self.frame,
                               height=BLOCK_HEIGHT,
                               width=2 + (BLOCK_WIDTH * 4),
                               state='disabled',
                               wrap='none')

        self.textbox.tag_configure("ascii", foreground="green")
        self.textbox.tag_configure("error", foreground="red")
        self.textbox.tag_configure("hexspace", foreground="navy")
        self.textbox.tag_configure("graybg", background="lightgray")
        yscroll = ttk.Scrollbar(self.frame, command=self.textbox.yview)
        self.textbox['yscrollcommand'] = yscroll.set
        yscroll.grid(row=1, column=7, sticky='ns')

        for column, widget in enumerate(
                (self.offset_label, self.offset_spinbox, self.encoding_label,
                 self.encoding_combobox)):
            widget.grid(row=0, column=column, sticky=tk.W)
        self.textbox.grid(row=1, column=0, columnspan=6, sticky='nsew')
        self.frame.grid(row=0, column=0, sticky='nsew')

        self.parent.bind("<Alt-f>", lambda *args: self.offset_spinbox.focus())
        self.parent.bind("<Alt-e>",
                         lambda *args: self.encoding_combobox.focus())
        for variable in (self.offset, self.encoding):
            variable.trace_variable("w", self.show_block)

    def show_block(self, *_):
        self.textbox.config(state='normal')
        self.textbox.delete("1.0", "end")
        if not self.filename:
            return
        with open(self.filename, "rb") as file:
            try:
                file.seek(self.offset.get(), os.SEEK_SET)
                block = file.read(BLOCK_SIZE)
            except Exception:  # Empty offsetSpinbox
                return
        rows = [
            block[i:i + BLOCK_WIDTH] for i in range(0, len(block), BLOCK_WIDTH)
        ]
        for row in rows:
            self.show_bytes(row)
            self.show_line(row)
        self.textbox.insert("end", "\n")
        self.textbox.config(state='disabled')

    def show_bytes(self, row):
        self.textbox.config(state='normal')
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
        self.textbox.config(state='disabled')

    def show_line(self, row):
        self.textbox.config(state='normal')
        for char in row.decode(self.encoding.get(), errors="replace"):
            tags = ()
            if char in "\u2028\u2029\t\n\r\v\f\uFFFD":
                char = "."
                tags = ("graybg" if char == "\uFFFD" else "error",)
            elif 0x20 < ord(char) < 0x7F:
                tags = ("ascii",)
            elif not 0x20 <= ord(char) <= 0xFFFF:  # Tcl/Tk limit
                char = "?"
                tags = ("error",)
            self.textbox.insert("end", char, tags)
        self.textbox.insert("end", "\n")
        self.textbox.config(state='disabled')

    def open(self, filename):
        if filename and os.path.exists(filename):
            self.parent.title("{} — {}".format(filename, "PyPlus"))
            size = os.path.getsize(filename)
            size = (size - BLOCK_SIZE if size > BLOCK_SIZE else size -
                                                                BLOCK_WIDTH)
            self.offset_spinbox.config(to=max(size, 0))
            self.filename = filename
            self.show_block()
