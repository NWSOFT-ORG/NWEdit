import mimetypes
import os
import time
import tkinter as tk
from tkinter import ttk

from src.Components.winframe import WinFrame
from src.constants import OSX, WINDOWS


class FileInfoDialog(WinFrame):
    def __init__(self, master: tk.Misc, path):
        self.path = path
        basename = os.path.basename(path)

        super().__init__(master, f"Info of {basename}")
        mdate = f"Last modified: {time.ctime(os.path.getmtime(path))}"
        cdate = f"Created: {time.ctime(os.path.getctime(path))}"
        mime_type = f"MIME: {self.mime_type}"

        ttk.Label(self, text=f"Name: {basename}").pack(
            side="top", anchor="nw", fill="x"
        )
        ttk.Label(self, text=f"Path: {path}").pack(side="top", anchor="nw", fill="x")
        ttk.Label(self, text=f"Size: {self.size}").pack(
            side="top", anchor="nw", fill="x"
        )
        ttk.Label(self, text=mime_type).pack(side="top", anchor="nw", fill="x")
        ttk.Separator(self).pack(fill="x")
        ttk.Label(self, text=mdate).pack(side="top", anchor="nw", fill="x")
        ttk.Label(self, text=cdate).pack(side="top", anchor="nw", fill="x")
        if not (WINDOWS or OSX):
            ttk.Label(
                self,
                text="Note: On Linux, the dates would not be the exact date of creation or modification!",
            ).pack(side="top", anchor="nw", fill="x")

    @property
    def mime_type(self) -> str:
        return mimetypes.guess_type(self.path)[0]

    @property
    def size(self) -> str:
        """Determine the correct unit"""
        size = str(os.path.getsize(self.path))
        if int(size) / 1024 < 1:
            size += " Bytes"
        elif int(size) / 1024 >= 1 <= 2:
            size = f"{int(size) // 1024} Kilobytes"
        elif int(size) / 1024**2 >= 1 <= 2:
            size = f"{int(size) // 1024 ** 2} Megabytes"
        elif int(size) / 1024**3 >= 1 <= 2:
            size = f"{int(size) // 1024 ** 3} Gigabytes"
        elif int(size) / 1024**4 >= 1 <= 2:
            size = f"{int(size) // 1024 ** 4} Terabytes"
        # It can go on and on, but the newest PCs won't have more than a PB storage
        #      /-------------/|
        #     /             / /
        #    /  SSD        / /
        #   /   10 TB     / /
        #  /             / /
        # /             / /
        # \=============\/
        return size
