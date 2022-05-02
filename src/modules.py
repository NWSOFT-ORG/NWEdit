"""All the necessary modules"""

import code
import codecs
import hashlib
import io
import logging
import mimetypes
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
import traceback
import urllib.request as request
import webbrowser
import zipfile
from keyword import iskeyword
from pathlib import Path

import art
import json5 as json
import pygments
import send2trash
import ttkthemes
from pygments import lexers, styles

if sys.platform == "darwin":
    import PyTouchBar


class EditorErr(Exception):
    """A nice exception class for debugging"""

    def __init__(self, message):
        # The error (e+m)
        super().__init__("An editor error is occurred." if not message else message)
