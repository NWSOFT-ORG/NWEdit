"""All the nessasary modules"""
import code
import hashlib
import io
import os
import platform
import queue
import shlex
import shutil
import subprocess
import sys
import threading
import tkinter as tk
import tkinter.filedialog
import tkinter.font as font
import tkinter.messagebox as messagebox
import tkinter.ttk as ttk
import webbrowser
from pathlib import Path

import json5 as json
import requests
import ttkthemes
from pygments import lexers
from pygments.lexers.python import PythonLexer
from pygments.styles import get_style_by_name
from pygson.json_lexer import JSONLexer
from ttkthemes import ThemedStyle

class EditorErr(Exception):
    """A nice exception class for debugging"""

    def __init__(self, message):
        # The error (e+m)
        super().__init__(
            'An editor error is occurred.' if not message else message)
