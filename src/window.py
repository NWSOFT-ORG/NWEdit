import tkinter as tk

from src.exceptions import NoWindowOpenError

__window = None
__initialized = False


def create_window():
    global __window, __initialized
    __window = tk.Tk()
    __initialized = True

    return __window


def get_window() -> tk.Tk:
    if __initialized and isinstance(__window, tk.Tk):
        return __window
    else:
        raise NoWindowOpenError()


def main_loop():
    if not __initialized:
        raise NoWindowOpenError()
    get_window().mainloop()
