"""Closable ttk.Notebook"""
import tkinter as tk
from tkinter import ttk

from src.Components.statusbar import bind_events
from src.constants import logger
from src.SettingsParser.general_settings import GeneralSettings
from src.Utils.images import get_image


class ClosableNotebook(ttk.Notebook):
    """A ttk Notebook with close buttons on each tab's
    image drawn by me using the mspaint app (the rubbish in many people's opinion)

    Change the layout, makes it look like this:
    +------------+
    | title   [X]|
    +-------------------------"""

    __initialized = False

    def __init__(self, master, cmd):
        self.style = ttk.Style()
        self.settings = GeneralSettings()
        self.bg = self.style.lookup("TLabel", "background")
        self.fg = self.style.lookup("TLabel", "foreground")
        if not self.__initialized:
            self.__initialize_custom_style()
        super().__init__(master=master, style="ClosableNotebook", takefocus=False)
        self.cmd = cmd

        self._active = None

        self.tab_frame = ttk.Frame(self)
        self.add_frame()

        self.bind("<1>", self.on_close_press, True)
        self.bind("<ButtonRelease-1>", self.on_close_release)
        self.bind("<B1-Motion>", self.move_tab)

    def add_frame(self):
        tab_frame = self.tab_frame
        tab_frame.place(relx=1.0, x=0, y=1, anchor="ne")

        ttk.Separator(tab_frame, orient="vertical").pack(side="left", fill="y", padx=2)

        prev_tab_label = ttk.Label(tab_frame, image=get_image("prev-tab"))
        prev_tab_label.bind("<1>", self.prevtab)
        prev_tab_label.pack(side="left")

        next_tab_label = ttk.Label(tab_frame, image=get_image("next-tab"))
        next_tab_label.bind("<1>", self.nexttab)
        next_tab_label.pack(side="left")

        ttk.Separator(tab_frame, orient="vertical").pack(side="left", fill="y", padx=2)

        allitems_label = ttk.Label(tab_frame, image=get_image("all-tabs"))
        allitems_label.bind("<1>", self.show_tab_menu)
        allitems_label.pack(side="left")

        bind_events(prev_tab_label)
        bind_events(next_tab_label)
        bind_events(allitems_label)

    def show_tab_menu(self, event):
        tab_menu = tk.Menu(self.master)
        for tab in self.tabs():
            tab_menu.add_command(
                label=self.tab(tab, option="text"),
                command=lambda temp=tab: self.select(temp),
            )
        tab_menu.tk_popup(event.x_root, event.y_root)

    def prevtab(self, _=None):
        try:
            self.select(self.index("current") - 1)
        except tk.TclError:
            pass

    def nexttab(self, _=None):
        try:
            self.select(self.index("current") + 1)
        except tk.TclError:
            pass

    def on_close_press(self, event):
        """Called when the button is pressed over the close button"""

        element = self.identify(event.x, event.y)
        if "close" in element:
            index = self.index(f"@{event.x},{event.y}")
            self.state(["pressed"])
            self._active = index
        else:
            self.event_generate("<<Notebook_B1-Down>>", when="tail")
        logger.debug("Close tab start")

    def on_close_release(self, event):
        """Called when the button is released over the close button"""
        try:
            if not self.instate(["pressed"]):
                return

            element = self.identify(event.x, event.y)
            index = self.index(f"@{event.x},{event.y}")

            if "close" in element and self._active == index:
                self.cmd(event)

            self.state(["!pressed"])
            self._active = None
            logger.debug("Close tab end")

        except tk.TclError:
            logger.exception("Error:")

    def __initialize_custom_style(self):
        self.style = style = ttk.Style()

        try:
            style.element_create(
                "close", "image", get_image("close"), border=10, sticky=""
            )
        except tk.TclError:
            pass
        style.layout(
            "ClosableNotebook",
            [
                (
                    "ClosableNotebook.client",
                    {
                        "sticky": "nswe",
                    },
                )
            ],
        )
        style.layout(
            "ClosableNotebook.Tab",
            [
                (
                    "ClosableNotebook.tab",
                    {
                        "sticky"  : "nswe",
                        "children": [
                            (
                                "ClosableNotebook.padding",
                                {
                                    "side"    : "top",
                                    "sticky"  : "nswe",
                                    "children": [
                                        (
                                            "ClosableNotebook.label",
                                            {"side": "left", "sticky": ""},
                                        ),
                                        (
                                            "ClosableNotebook.close",
                                            {"side": "left", "sticky": ""},
                                        ),
                                    ],
                                },
                            )
                        ],
                    },
                )
            ],
        )
        logger.debug("Initialized custom style.")

    def move_tab(self, event: tk.Event) -> None:
        if self.index("end") > 1:
            y = self.get_tab.winfo_y() - 5

            try:
                self.insert(event.widget.index(f"@{event.x},{y}"), self.select())
            except tk.TclError:
                return

    @property
    def get_tab(self) -> tk.Widget:
        return self.nametowidget(self.select())
