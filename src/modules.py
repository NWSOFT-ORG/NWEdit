"""All the nessasary modules"""
# pylint: disable-all
# flake8: noqa

import code
import codecs
import hashlib
import io
import logging
import os
import platform
import queue
import shlex
import shutil
import subprocess
import sys
import threading
import time
import tkinter as tk
import tkinter.font as font
import tkinter.ttk as ttk
import webbrowser
import zipfile
from pathlib import Path

import json5 as json
import requests
import ttkthemes
import pygments
from pygments import lexers
from pygments import styles

if sys.platform == "darwin":
    import PyTouchBar


class ScrolledFrame(ttk.Frame):
    """A pure Tkinter scrollable frame that actually works!
    * Use the 'interior' attribute to place widgets inside the scrollable frame
    * Construct and pack/place/grid normally
    * This frame only allows vertical scrolling

    """

    def __init__(self, parent, *args, **kw):
        super().__init__(parent, *args, **kw)

        # create a canvas object and a vertical scrollbar for scrolling it
        scrollbar = ttk.Scrollbar(self, orient="horizontal")
        scrollbar.pack(fill="x", side="bottom")
        canvas = tk.Canvas(
            self, bd=0, highlightthickness=0, xscrollcommand=scrollbar.set, height=50
        )
        canvas.pack(fill='both', expand=1)
        scrollbar.config(command=canvas.xview)

        # create a frame inside the canvas which will be scrolled with it
        self.interior = interior = ttk.Frame(canvas, height=50)
        canvas.create_window(0, 0, window=interior, anchor="nw")

        def _configure_interior(_):
            # update the scrollbars to match the size of the inner fram
            size = (interior.winfo_reqwidth(), interior.winfo_reqheight())
            canvas.config(scrollregion="0 0 %s %s" % size)
            if interior.winfo_reqwidth() != canvas.winfo_width():
                # update the canvas's width to fit the inner fram
                canvas.config(width=interior.winfo_reqwidth())

        interior.bind("<Configure>", _configure_interior)


class EditorErr(Exception):
    """A nice exception class for debugging"""

    def __init__(self, message):
        # The error (e+m)
        super().__init__("An editor error is occurred." if not message else message)