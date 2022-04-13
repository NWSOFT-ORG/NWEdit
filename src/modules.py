"""All the necessary modules"""

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
import urllib.request as request
from pathlib import Path

import json5 as json
import ttkthemes
import pygments
from pygments import lexers
from pygments import styles
from keyword import iskeyword
import art
import send2trash
import mimetypes
import traceback

if sys.platform == "darwin":
    import PyTouchBar


class EditorErr(Exception):
    """A nice exception class for debugging"""

    def __init__(self, message):
        # The error (e+m)
        super().__init__("An editor error is occurred." if not message else message)