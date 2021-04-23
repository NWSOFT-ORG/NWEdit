"""All the nessasary modules"""
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
import tkinter.filedialog
import tkinter.font as font
import tkinter.ttk as ttk
import webbrowser
import zipfile
from pathlib import Path

import json5 as json
import requests
import ttkthemes
from pygments import lexers
from pygments.styles import get_style_by_name
from pygson.json_lexer import JSONLexer
from ttkthemes import ThemedStyle

if sys.platform == "darwin":
    import PyTouchBar


class ScrolledFrame(ttk.Frame):
    """A pure Tkinter scrollable frame that actually works!
    * Use the 'interior' attribute to place widgets inside the scrollable frame
    * Construct and pack/place/grid normally
    * This frame only allows vertical scrolling

    """
    def __init__(self, parent, *args, **kw):
        ttk.Frame.__init__(self, parent, *args, **kw)            

        # create a canvas object and a vertical scrollbar for scrolling it
        xscrollbar = ttk.Scrollbar(self, orient='horizontal')
        xscrollbar.pack(fill='x', side='bottom')
        canvas = tk.Canvas(self, bd=0, highlightthickness=0,
                        xscrollcommand=xscrollbar.set, height=10)
        canvas.pack(side='left', fill='both', expand=1)
        xscrollbar.config(command=canvas.xview)

        # reset the view
        canvas.xview_moveto(0)
        canvas.yview_moveto(0)

        # create a frame inside the canvas which will be scrolled with it
        self.interior = interior = ttk.Frame(canvas)
        interior_id = canvas.create_window(0, 0, window=interior,
                                           anchor='nw', height=10)

        # track changes to the canvas and frame width and sync them,
        # also updating the scrollbar
        def _configure_interior(event):
            # update the scrollbars to match the size of the inner frame
            size = (interior.winfo_reqwidth(), interior.winfo_reqheight())
            canvas.config(scrollregion="0 0 %s %s" % size)
            if interior.winfo_reqwidth() != canvas.winfo_width():
                # update the canvas's width to fit the inner frame
                canvas.config(width=interior.winfo_reqwidth())
        interior.bind('<Configure>', _configure_interior)

        def _configure_canvas(event):
            if interior.winfo_reqwidth() != canvas.winfo_width():
                # update the inner frame's width to fill the canvas
                canvas.itemconfigure(interior_id, width=canvas.winfo_width())
        canvas.bind('<Configure>', _configure_canvas)

class EditorErr(Exception):
    """A nice exception class for debugging"""

    def __init__(self, message):
        # The error (e+m)
        super().__init__("An editor error is occurred." if not message else message)
