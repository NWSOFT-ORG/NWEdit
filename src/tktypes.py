"""Typings for editor"""

import tkinter as tk
from typing import Union

Tk_Win = Union[tk.Tk, tk.Toplevel]
Tk_Widget = Union[Tk_Win, tk.Misc, tk.Widget, tk.BaseWidget]
