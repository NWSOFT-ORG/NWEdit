"""Useful functions"""

import tkinter as tk
from keyword import iskeyword
from typing import Union

from pygments import styles
from tkterminal import Terminal

from src.constants import ILLEGAL_CHARS, ILLEGAL_NAMES, WINDOWS, textchars
from src.SettingsParser.general_settings import GeneralSettings
from src.Utils.color_utils import darken_color, is_dark_color, lighten_color


def is_binary_string(byte: bytes) -> bool:
    return bool(byte.translate(None, textchars))


def is_valid_name(name) -> bool:
    return name.isidentifier() and not iskeyword(name)


def shell_command(command, cwd="~"):
    window = tk.Toplevel()
    terminal = Terminal(window, padx=5, pady=5)
    apply_style(terminal)
    terminal.shell = True
    terminal.basename = "$ " if not WINDOWS else "> "
    terminal.run_command(f"cd {cwd}")
    terminal.clear()
    terminal.run_command(command)
    terminal.pack(fill="both", expand=True)


def open_shell(frame: tk.Misc):
    terminal = Terminal(frame, padx=5, pady=5)
    apply_style(terminal)
    terminal.shell = True
    terminal.basename = "$ " if not WINDOWS else "> "
    return terminal


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


def apply_style(text: tk.Text):
    settings_class = GeneralSettings()
    font_face = settings_class.get_font()
    style = styles.get_style_by_name(settings_class.get_settings("pygments_theme"))
    bgcolor = style.background_color
    fgcolor = style.highlight_color
    if is_dark_color(bgcolor):
        bg = lighten_color(bgcolor, 30)
        fg = lighten_color(fgcolor, 40)
    else:
        bg = darken_color(bgcolor, 30)
        fg = darken_color(fgcolor, 40)
    text.config(
        bg=bgcolor,
        fg=fgcolor,
        selectforeground=bg,
        selectbackground=fgcolor,
        insertbackground=fg,
        highlightthickness=0,
        font=font_face,
        wrap="none",
        insertwidth=3,
        maxundo=-1,
        autoseparators=True,
        undo=True,
    )
