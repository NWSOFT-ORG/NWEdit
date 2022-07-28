"""Useful functions"""

import tkinter as tk
from keyword import iskeyword
from typing import Union

from tkterminal import Terminal

from src.constants import textchars

DARK_COLOR = 128

ILLEGAL_CHARS = ('\\', '/', ' ', '~') + ('?', '<', '>', '|', '*', ':')  # Windows illegal filenames
ILLEGAL_NAMES = (
    "com1", "com2", "com3", "com4", "com5", "com6", "com7", "com8", "com9", "lpt1", "lpt2", "lpt3", "lpt4", "lpt5",
    "lpt6",
    "lpt7", "lpt8", "lpt9", "con", "nul", "prn", '.', '..', '...', '')


def is_binary_string(byte: bytes) -> bool:
    return bool(byte.translate(None, textchars))


def is_valid_name(name) -> bool:
    return name.isidentifier() and not iskeyword(name)


def shell_command(command, cwd="~"):
    window = tk.Toplevel()
    terminal = Terminal(window, padx=5, pady=5)
    terminal.shell = True
    terminal.run_command(f"cd {cwd}")
    terminal.run_command(command)
    terminal.pack(fill="both", expand=True)


def open_shell():
    window = tk.Toplevel()
    terminal = Terminal(window, padx=5, pady=5)
    terminal.shell = True
    terminal.pack(fill="both", expand=True)


def is_illegal_filename(name: str) -> Union[None, bool]:
    if len(name) > 31:
        # Not recommended. Too hard to memorise!
        return None
    if not name.isascii():
        # Non-ASCII files might mess up the system
        return True
    if name.endswith('.'):
        return True  # Supported, but Windows Shell won't show it
    for illegal in ILLEGAL_CHARS:
        if illegal in name:
            return True
    for illegal in ILLEGAL_NAMES:
        if illegal.lower() == name.lower():
            return True
    return False
