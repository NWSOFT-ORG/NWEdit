"""A ribbon tool meant to simulate the Microsoft Ribbon UX design"""

import tkinter as tk
from tkinter import ttk
from tkinter.font import Font
from typing import *


def font_height():
    return Font().metrics("linespace")


class GroupLabel(ttk.Label):
    def __init__(self, parent, text):
        super().__init__(parent, text=text, padding="10 5")


class Group:
    buttons: Dict[Text, Dict[Text, Union[tk.Image, None, Callable]]] = {}
    big_buttons: Dict[Text, Dict[Text, Union[tk.Image, None, Callable]]] = {}

    def add_small_button(
        self, text: str, image: Union[tk.Image, None] = None, command: Callable = None
    ):
        if text in self.buttons.keys():
            raise ValueError("Button already exsists")
        self.buttons[text] = {"image": image, "command": command}

    def add_big_button(
        self,
        text: str = "",
        image: Union[tk.Image, None] = None,
        command: Callable = None,
    ):
        if text in self.big_buttons.keys():
            raise ValueError("Button already exsists")
        self.big_buttons[text] = {"image": image, "command": command}


class Page:
    def __init__(self, name, frame):
        self.name = name
        self.frame = frame


class Ribbon(ttk.Notebook):
    def __init__(self, parent: tk.Misc):
        super().__init__(parent, style="Ribbon.TNotebook")
        self.__init_custom_style()
        self.tabs: Dict[str, Page] = {}
        self.pack(side="top", fill="x")

    def add_page(self, name):
        frame = ttk.Frame(self)
        self.tabs[name] = Page(name, frame)
        frame.pack(fill="both")
        self.add(frame, text=name)

    def add_group(self, group: Group, name: str, tab: str):
        name = name.upper()
        parent = self.tabs[tab].frame

        group_label = GroupLabel(parent, text=name)
        frame = ttk.LabelFrame(parent, labelwidget=group_label, labelanchor="s")
        frame.pack(side="left", padx=5, pady=5)

        buttons = group.buttons
        for row, item in enumerate(buttons.keys()):
            ttk.Button(
                frame,
                text=item,
                image=buttons[item]["image"],
                command=buttons[item]["command"],
            ).grid(column=0, row=row)

        big_buttons = group.big_buttons
        for column, item in enumerate(big_buttons.keys()):
            button = ttk.Button(
                frame,
                text=item,
                image=big_buttons[item]["image"],
                command=big_buttons[item]["command"],
            )
            button.grid_propagate(False)
            button.grid(column=1 + column, row=0, rowspan=3, sticky="nsew")

    def __init_custom_style(self):
        self.tab_style = ttk.Style(self)
        self.tab_style.theme_use(
            "alt"
        )  # The Aqua theme for OSX is not working great for the ribbon design
        self.tab_style.configure("Ribbon.TNotebook", tabposition="nw")


def callback_small():
    print("Hello from a small button")


def callback_big():
    print("Hello from a big button")


def main():
    root = tk.Tk()
    r = Ribbon(root)
    group = Group()
    group.add_small_button("Hello", command=callback_small)
    group.add_small_button("Hello1", command=callback_small)
    group.add_small_button("Hello2", command=callback_small)
    group.add_big_button("Hello", command=callback_big)
    group.add_big_button("Hello1", command=callback_big)
    r.add_page("File")
    r.add_group(group, "Hello", "File")
    r.add_page("Click me!")
    root.mainloop()


if __name__ == "__main__":
    main()
