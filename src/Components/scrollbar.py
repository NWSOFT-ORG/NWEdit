import tkinter as tk
from tkinter import ttk
from typing import Callable, Literal

from src.Utils.color_utils import darken_color, lighten_color


class Scrollbar(tk.Canvas):
    """
    A scrollbar is packed as a sibling of what it's scrolling.
    """

    def __init__(
        self,
        parent,
        command: Callable,
        orient: Literal["vertical", "horizontal"] = "vertical",
        width=20,
    ):
        self.command = command
        super().__init__(parent)

        self.orient = orient

        self.new_start_y = 0
        self.new_start_x = 0
        self.first_y = 0
        self.first_x = 0

        style = ttk.Style()
        bg = style.lookup("TLabel", "background")
        self.slidercolor = lighten_color(bg, 30)
        self.fill_color = darken_color(bg, 10)

        if orient == "vertical":
            self.config(
                bg=self.fill_color, bd=0,
                highlightthickness=0, width=width
            )
        else:
            self.config(
                bg=self.fill_color, bd=0,
                highlightthickness=0, height=width
            )

        # coordinates are irrelevant; they will be recomputed
        #   in the 'set' method
        self.create_rectangle(
            0, 0, 1, 1, fill=self.slidercolor, tags=("slider",), outline=""
        )
        self.bind("<ButtonPress-1>", self.move_on_click)

        self.bind("<ButtonPress-1>", self.start_scroll, add="+")
        self.bind("<B1-Motion>", self.move_on_scroll)
        self.bind("<ButtonRelease-1>", self.end_scroll)

    def set(self, lo, hi):
        lo = float(lo)
        hi = float(hi)

        height = self.winfo_height()
        width = self.winfo_width()

        if self.orient == "vertical":
            x0 = 2
            y0 = max(int(height * lo), 0)
            x1 = width - 2
            y1 = min(int(height * hi), height)
        # This was the tricky part of making a horizontal scrollbar
        #   when I already knew how to make a vertical one.
        #   You can't just change all the "height" to "width"
        #   and "y" to "x". You also have to reverse what x0 etc
        #   are equal to, comparing code in if and elif. Till that was
        #   done, everything worked but the horizontal scrollbar's
        #   slider moved up & down.
        elif self.orient == "horizontal":
            x0 = max(int(width * lo), 0)
            y0 = 2
            x1 = min(int(width * hi), width)
            y1 = height
        else:
            raise ValueError("orient must be 'vertical' or 'horizontal'")

        self.coords("slider", x0, y0, x1, y1)
        self.x0 = x0
        self.y0 = y0
        self.x1 = x1
        self.y1 = y1

    def get(self):
        return (self.y0, self.y1)

    def move_on_click(self, event):
        if self.orient == "vertical":
            # don't scroll on click if mouse pointer is w/in slider
            y = event.y / self.winfo_height()
            if event.y < self.y0 or event.y > self.y1:
                self.command("moveto", y)
            # get starting position of a scrolling event
            else:
                self.first_y = event.y
        elif self.orient == "horizontal":
            # do nothing if mouse pointer is w/in slider
            x = event.x / self.winfo_width()
            if event.x < self.x0 or event.x > self.x1:
                self.command("moveto", x)
            # get starting position of a scrolling event
            else:
                self.first_x = event.x

    def start_scroll(self, event):
        if self.orient == "vertical":
            self.last_y = event.y
            self.y_move_on_click = int(event.y - self.coords("slider")[1])
        elif self.orient == "horizontal":
            self.last_x = event.x
            self.x_move_on_click = int(event.x - self.coords("slider")[0])

    def end_scroll(self, event):
        if self.orient == "vertical":
            self.new_start_y = event.y
        elif self.orient == "horizontal":
            self.new_start_x = event.x

    def move_on_scroll(self, event):
        """Only scroll if the mouse moves a few pixels. This makes
        the click-in-trough work right even if the click smears
        a little. Otherwise, a perfectly motionless mouse click
        is the only way to get the trough click to work right.
        Setting jerkiness to 5 or more makes very sloppy trough
        clicking work, but then scrolling is not smooth. 3 is OK."""

        jerkiness = 3

        if self.orient == "vertical":
            if abs(event.y - self.last_y) < jerkiness:
                return
            # scroll the scrolled widget in proportion to mouse motion
            #   compute whether scrolling up or down
            delta = 1 if event.y > self.last_y else -1
            #   remember this location for the next time this is called
            self.last_y = event.y
            #   do the scroll
            self.command("scroll", delta, "units")
            # afix slider to mouse pointer
            mouse_pos = event.y - self.first_y
            if self.new_start_y != 0:
                mouse_pos = event.y - self.y_move_on_click
            self.command("moveto", mouse_pos / self.winfo_height())
        elif self.orient == "horizontal":
            if abs(event.x - self.last_x) < jerkiness:
                return
            # scroll the scrolled widget in proportion to mouse motion
            #   compute whether scrolling left or right
            delta = 1 if event.x > self.last_x else -1
            #   remember this location for the next time this is called
            self.last_x = event.x
            #   do the scroll
            self.command("scroll", delta, "units")
            # afix slider to mouse pointer
            mouse_pos = event.x - self.first_x
            if self.new_start_x != 0:
                mouse_pos = event.x - self.x_move_on_click
            self.command("moveto", mouse_pos / self.winfo_width())


class TextScrollbar(Scrollbar):
    def __init__(
        self,
        parent,
        command: callable,
        widget: tk.Text,
        orient: Literal["vertical", "horizontal"] = "vertical",
    ):
        super().__init__(parent, command, orient=orient)
        self.config(bg=widget["bg"])
        self.itemconfig("slider", fill=widget["fg"])
