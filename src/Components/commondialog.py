import os
import tkinter as tk
import urllib.error
import webbrowser
from tkinter import ttk
from typing import *
from urllib import request

import json5 as json

from src.Components.tkentry import Entry
from src.Components.winframe import WinFrame
from src.constants import VERSION, logger
from src.types import Tk_Widget, Tk_Win
from src.Utils.images import get_image


def download_file(url: str, localfile: os.PathLike = "") -> str:
    """Downloads a file from remote path"""
    localfile = url.split("/")[-1] if not localfile else localfile
    request.urlretrieve(url, localfile)
    return localfile


class YesNoDialog(WinFrame):
    def __init__(
        self, parent: Tk_Win = None, title: str = "", text: str = None
    ) -> None:
        self.text = text
        super().__init__(parent, title, icon=get_image("question"))
        label1 = ttk.Label(self, text=self.text)
        label1.pack(fill="both")

        box = ttk.Frame(self)

        b1 = ttk.Button(box, text="Yes", command=self.apply)
        b1.pack(side="left")
        b2 = ttk.Button(box, text="No", command=self.cancel)
        b2.pack(side="left")

        box.pack(fill="x")
        self.result = 0
        self.protocol("WM_DELETE_WINDOW", self.cancel)
        self.wait_window(self)

    def apply(self, _=None) -> None:
        self.result = 1
        self.destroy()
        logger.info("apply")

    def cancel(self, _=None) -> None:
        """put focus back to the parent window"""
        self.result = 0
        self.destroy()
        logger.info("cancel")


class StringInputDialog(WinFrame):
    def __init__(
        self,
        parent: Tk_Widget = ".",
        title: str = "",
        text: str = "",
    ) -> None:
        super().__init__(parent, title, icon=get_image("question"))
        self.result = ""
        ttk.Label(self, text=text).pack(fill="x")
        self.entry = Entry(self)
        self.entry.pack(fill="x", expand=1)
        box = ttk.Frame(self)

        b1 = ttk.Button(box, text="OK", command=self.apply)
        b1.pack(side="left")
        b2 = ttk.Button(box, text="Cancel", command=self.cancel)
        b2.pack(side="left")

        box.pack(fill="x")
        self.protocol("WM_DELETE_WINDOW", self.cancel)
        self.wait_window(self)

    def apply(self) -> None:
        self.result = self.entry.get()
        self.destroy()
        logger.info("apply")

    def cancel(self) -> None:
        self.result = ""
        self.destroy()
        logger.info("cancel")


class ErrorInfoDialog(WinFrame):
    def __init__(
        self,
        parent: Tk_Widget = None,
        text: str = None,
        title: str = "Error",
    ) -> None:
        self.text = text
        super().__init__(parent, title, icon=get_image("question"))
        label1 = ttk.Label(self, text=self.text)
        label1.pack(side="top", fill="both", expand=1)
        b1 = ttk.Button(self, text="OK", width=10, command=self.apply)
        b1.pack(side="left")
        self.wait_window(self)

    def apply(self, _: tk.Event = None) -> None:
        self.destroy()
        logger.info("apply")


class AboutDialog:
    def __init__(self, master: Tk_Win) -> None:
        """Shows the version and related info of the editor."""
        self.master = master

        window = WinFrame(self.master, "About PyPlus", icon=get_image("info"))
        ver = ttk.Frame(window)
        window.add_widget(ver)
        ttk.Label(ver, image=get_image("pyplus-35px", img_type="image")).pack(
            fill="both"
        )
        ttk.Label(ver, text=f"Version {VERSION}", font="tkDefaultFont 30 bold").pack(
            fill="both"
        )
        if self.check_updates(popup=False)[0] is None:
            ttk.Label(ver, text="Unable to check updates").pack(fill="both")
        elif self.check_updates(popup=False)[0]:
            update = ttk.Label(
                ver, text="Updates available", foreground="blue", cursor="hand2"
            )
            update.pack(fill="both")
            update.bind(
                "<Button-1>",
                lambda e: webbrowser.open_new_tab(self.check_updates(popup=False)[1]),
            )
        else:
            ttk.Label(ver, text="No updates available").pack(fill="both")

    def check_updates(self, popup: bool = True) -> List:
        if "DEV" in VERSION:
            ErrorInfoDialog(
                text="Updates aren't supported by develop builds,\n\
            since you're always on the latest version!",
            )  # If you're on the developer build, you don't need updates!
            return [True, "about:blank"]
        try:
            download_file(
                url="https://raw.githubusercontent.com/ZCG-coder/NWSOFT/master/PyPlusWeb/ver.json"
            )
        except urllib.error.URLError:
            return [None, "about:blank"]
        with open("ver.json") as f:
            newest = json.load(f)
        version = newest["version"]
        if not popup:
            os.remove("ver.json")
            return [version != VERSION, newest["url"]]
        updatewin = WinFrame(
            self.master, "Updates", closable=False, icon=get_image("info")
        )
        frame = ttk.Frame(updatewin)
        updatewin.add_widget(frame)
        if version != VERSION:
            ttk.Label(
                frame, text="Update available!", font="tkDefaultFont 30"
            ).pack(fill="both")
            ttk.Label(frame, text=version).pack(fill="both")
            ttk.Label(frame, text=newest["details"]).pack(fill="both")
            url = newest["url"]
            ttk.Button(
                frame, text="Get this update", command=lambda: webbrowser.open(url)
            ).pack()
        else:
            ttk.Label(
                frame, text="No updates available", font="tkDefaultFont 30"
            ).pack(fill="both")
        os.remove("ver.json")
