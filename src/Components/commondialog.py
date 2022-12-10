import tkinter as tk
import urllib.error
import webbrowser
from tkinter import ttk
from typing import List
from urllib import request

import json5rw as json

from src.Components.link import Link
from src.Components.tkentry import Entry
from src.Components.winframe import WinFrame
from src.constants import logger, VERSION
from src.tktypes import Tk_Widget, Tk_Win
from src.Utils.images import get_image
from src.window import get_window


def download_file(url: str) -> str:
    """Downloads a file from remote path"""
    with request.urlopen(url) as f:
        content = f.read().decode("utf-8")
    return content


class YesNoDialog(WinFrame):
    def __init__(
        self, master: Tk_Win = None, title: str = "", text: str = None
    ) -> None:
        if master is None:
            master = get_window()
        self.text = text
        super().__init__(master, title, icon=get_image("question"))
        label1 = ttk.Label(self, text=self.text)
        label1.pack(fill="both")

        box = ttk.Frame(self)

        b1 = ttk.Button(box, text="Yes", command=self.apply, default="active")
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
        """put focus back to the master window"""
        self.result = 0
        self.destroy()
        logger.info("cancel")


class StringInputDialog(WinFrame):
    def __init__(
        self,
        master: Tk_Widget = None,
        title: str = "",
        text: str = "",
    ) -> None:
        if master is None:
            master = get_window()
        super().__init__(master, title, icon=get_image("question"))
        self.result = ""
        ttk.Label(self, text=text).pack(fill="x")
        self.entry = Entry(self)
        self.entry.pack(fill="x", expand=1)
        box = ttk.Frame(self)

        b1 = ttk.Button(box, text="OK", command=self.apply, default="active")
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
        master: Tk_Widget = None,
        text: str = None,
        title: str = "Error",
    ) -> None:
        if master is None:
            master = get_window()
        self.text = text
        super().__init__(master, title, icon=get_image("question"))
        label1 = ttk.Label(self, text=self.text)
        label1.pack(side="top", fill="both", expand=1)
        b1 = ttk.Button(self, text="OK", width=10, command=self.apply, default="active")
        b1.pack(side="left")
        self.wait_window(self)

    def apply(self, _: tk.Event = None) -> None:
        self.destroy()
        logger.info("apply")


class AboutDialog:
    def __init__(self, master: Tk_Win) -> None:
        """Shows the version and related info of the editor."""
        self.master = master

        window = WinFrame(self.master, "About NWEdit", icon=get_image("info"))
        ver = ttk.Frame(window)
        window.add_widget(ver)
        self.icon_35px = get_image("NWEdit", "custom", 35, 35)
        version = ttk.Label(
            ver,
            text=f"Version {VERSION}",
            font="tkDefaultFont 35 bold",
            image=self.icon_35px,
            compound="left"
        )
        version.img = self.icon_35px
        version.pack(
            fill="both"
        )
        if self.check_updates(popup=False)[0] is None:
            ttk.Label(ver, text="Unable to check updates").pack(fill="both")
        elif self.check_updates(popup=False)[0]:
            update = Link(
                ver, text="Updates available",
                command=lambda _: webbrowser.open_new_tab(self.check_updates(popup=False)[1])
            )
            update.pack(fill="both")
        else:
            ttk.Label(ver, text="No updates available").pack(fill="both")

    def check_updates(self, popup: bool = True) -> List:
        if "DEV" in VERSION and popup:
            ErrorInfoDialog(
                text="Updates aren't supported by develop builds,\n\
            since you're always on the latest version!"
            )  # If you're on the developer build, you don't need updates!
            return [True, "about:blank"]
        try:
            newest = download_file(url="https://pst.klgrth.io/paste/7fv2t/download")
            newest = json.loads(newest)
        except urllib.error.URLError:
            logger.exception("Unable to check updates")
            return [None, "about:blank"]
        if newest is None:
            return [None, "about:blank"]

        version = newest["version"]
        details = newest["details"]
        update_available = version != VERSION
        url = newest["url"]

        if not popup:
            return [update_available, url]
        updatewin = WinFrame(
            self.master, "Updates", closable=False, icon=get_image("info")
        )
        frame = ttk.Frame(updatewin)
        updatewin.add_widget(frame)
        if update_available:
            ttk.Label(
                frame, text="Update available!", font="tkDefaultFont 30"
            ).pack(fill="both")
            ttk.Label(frame, text=version).pack(fill="both")
            ttk.Label(frame, text=details).pack(fill="both")
            ttk.Button(
                frame, text="Get this update", command=lambda: webbrowser.open(url)
            ).pack()
        else:
            ttk.Label(
                frame, text="No updates available", font="tkDefaultFont 30"
            ).pack(fill="both")
