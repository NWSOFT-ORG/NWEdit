from typing import *

from src.modules import tk

Tk_Win = Union[tk.Tk, tk.Toplevel, Literal["."]]
Tk_Widget = Union[Tk_Win, tk.Misc, tk.Widget, tk.BaseWidget]
