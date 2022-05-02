"""Useful functions"""

from tkterminal import Terminal

from src.constants import textchars
from src.modules import iskeyword, tk

DARK_COLOR = 128


def is_binary_string(byte) -> bool:
    return bool(byte.translate(None, textchars))


def is_valid_name(name) -> bool:
    return name.isidentifier() and not iskeyword(name)


def shell_command(command, cwd="~"):
    window = tk.Toplevel()
    terminal = Terminal(window, padx=5, pady=5)
    terminal.shell = True
    terminal.run_command(command)
    terminal.pack(fill="both", expand=True)


def open_shell():
    window = tk.Toplevel()
    terminal = Terminal(window, padx=5, pady=5)
    terminal.shell = True
    terminal.pack(fill="both", expand=True)
