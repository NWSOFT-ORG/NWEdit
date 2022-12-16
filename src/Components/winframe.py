import tkinter as tk
from tkinter import font, ttk

import json5rw as json

from src.constants import OSX
from src.tktypes import Tk_Win
from src.Utils.color_utils import lighten_color
from src.Utils.images import get_image
from src.Utils.photoimage import IconImage

RADIUS = 27 if OSX else 0


# Need these because importing settings is a circular import
def get_theme():
    with open("Config/general-settings.json") as f:
        settings = json.load(f)
        if not settings:
            return ""  # Default theme
    return settings["theme"]


def get_bg():
    style = ttk.Style()
    return style.lookup("TLabel", "background")


def get_fg():
    style = ttk.Style()
    return style.lookup("TLabel", "foreground")


def font_height():
    return font.Font(font="tkDefaultFont").metrics("linespace")


def round_rect(canvas, x1, y1, x2, y2, radius=25, **kwargs):
    points = [x1 + radius, y1,
              x1 + radius, y1,
              x2 - radius, y1,
              x2 - radius, y1,
              x2, y1,
              x2, y1 + radius,
              x2, y1 + radius,
              x2, y2 - radius,
              x2, y2 - radius,
              x2, y2,
              x2 - radius, y2,
              x2 - radius, y2,
              x1 + radius, y2,
              x1 + radius, y2,
              x1, y2,
              x1, y2 - radius,
              x1, y2 - radius,
              x1, y1 + radius,
              x1, y1 + radius,
              x1, y1]

    return canvas.create_polygon(points, **kwargs, smooth=True)


class WinFrame(tk.Toplevel):
    child_frame = None
    x = 0
    y = 0

    def __init__(
            self,
            master: Tk_Win,
            title: str,
            disable: bool = True,
            closable: bool = True,
            resizable: bool = True,
            icon: IconImage = None,
    ):
        super().__init__(master)
        self.overrideredirect(True)
        self.icon = icon
        self.title_text = title
        super().title(title)  # Need a decent message to show on the taskbar
        self.update_idletasks()
        self.titlebar = tk.Canvas(
            self,
            bd=0,
            highlightthickness=0,
            height=font_height() * 1.5,
            width=self.winfo_width()
        )
        self.status_bar = tk.Canvas(
            self,
            bd=0,
            highlightthickness=0,
            height=font_height() * 1.5,
            width=self.winfo_width(),
            takefocus=True
        )
        if OSX:
            self.titlebar["bg"] = self.status_bar["bg"] = "systemTransparent"
            # The transparent color exists in OSX only
        self.titlebar.pack(fill="x", side="top")
        self.master = master
        self.bg = get_bg()
        if closable:
            self.close_button()
            self.bind("<Escape>", lambda _: self.destroy())
        self.window_bindings()
        self.wait_visibility(self)  # Fix focus issues

        if disable:
            self.grab_set()  # Linux WMs might fail to grab the window

        self.lift()
        if OSX:
            # On OSX, all windows have rounded corners. Need to make window transparent before switching
            self.wm_attributes("-transparent", True)
        self.bind("<Destroy>", self.on_exit)
        self.bind("<Configure>", self.create_bar)
        self._resizable = resizable

        self.create_bar()

    def create_bar(self, _=None):
        self.create_statusbar()
        self.create_titlebar()

    def create_statusbar(self):
        self.status_bar.delete("status")

        self.status_bar.pack(side="bottom", fill="x")
        self.update_idletasks()

        round_rect(
            self.status_bar, 0, -self.status_bar.winfo_height(),
            self.status_bar.winfo_width(), self.status_bar.winfo_height(), RADIUS,
            fill=get_bg(), tags="status"
        )
        if self._resizable:
            if OSX:
                self.status_bar.create_arc(
                    self.winfo_width() - self.status_bar.winfo_height(),
                    0,
                    self.winfo_width(),
                    self.winfo_height(),
                    fill=lighten_color(get_bg(), 40),
                    outline="",
                    start=-90,
                    tags="size"
                )
            else:
                self.status_bar.create_rectangle(
                    self.winfo_width() - self.status_bar.winfo_height(), 0,
                    self.winfo_width(),
                    self.winfo_height(),
                    fill=lighten_color(get_bg(), 40),
                    outline="",
                    tags="size"
                )
            self.status_bar.tag_bind("size", "<B1-Motion>", self.resize)

    def on_exit(self, _):
        # Release Grab to prevent issues
        self.grab_release()

    def create_titlebar(self, _=None):
        self.titlebar.delete('all')
        self.update_idletasks()
        self.titlebar.update_idletasks()
        round_rect(
            self.titlebar,
            0,
            0,
            self.winfo_width(),
            self.titlebar.winfo_height() * 2,
            RADIUS,
            fill=get_bg()
        )
        self.titlebar.create_image(
            20, int((self.titlebar.winfo_height() - 16) / 2), image=self.icon, anchor="nw"
        )
        self.titlebar.create_text(
            40, int((self.titlebar.winfo_height() - font_height()) / 2), text=self.title_text,
            fill=get_fg(), anchor="nw"
        )
        self.close_button()

    def add_widget(self, child_frame: tk.Widget):
        self.child_frame = child_frame
        self.child_frame.pack(fill="both", expand=True)
        self.child_frame.update_idletasks()
        self.titlebar["width"] = self.child_frame.winfo_width()
        self.create_titlebar()

    def window_bindings(self):
        self.titlebar.bind("<ButtonPress-1>", self.start_move)
        self.titlebar.bind("<ButtonRelease-1>", self.stop_move)
        self.titlebar.bind("<B1-Motion>", self.do_move)

    def wm_resizable(self, width: bool = ..., height: bool = ...):
        self._resizable = bool(width or height)
        super().resizable(width, height)

    resizable = wm_resizable

    def start_move(self, event):
        self.x = event.x
        self.y = event.y

    def stop_move(self, _):
        self.x = None
        self.y = None

    def do_move(self, event):
        x = event.x - self.x + self.winfo_x()
        y = event.y - self.y + self.winfo_y()
        self.geometry(f"+{x}+{y}")

    def resize(self, event: tk.Event):
        cursor_x = event.x_root
        cursor_y = event.y_root
        window_x = self.winfo_rootx()
        window_y = self.winfo_rooty()
        if (cursor_y > window_y) and (cursor_x > window_x):
            self.geometry(f"{cursor_x - window_x}x{cursor_y - window_y}")
            # Recreate title
            self.create_titlebar()
            self.create_statusbar()
        return

    def close_button(self):
        image = get_image("close")
        if not image:
            return
        self.titlebar.image = image

        y = int((self.status_bar.winfo_height() - image.height()) / 2)

        btn = self.titlebar.create_image(5, y, anchor="nw", image=image)
        self.titlebar.tag_bind(btn, "<ButtonRelease-1>", lambda _: self.destroy())
