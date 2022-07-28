import os
import sys
import tkinter as tk
from tkinter import font, ttk
from typing import *

import json5 as json
import ttkthemes

from src.constants import logger, OSX
from src.editor import Editor
from src.project import ProjectView
from src.SettingsParser.general_settings import GeneralSettings
from src.SettingsParser.project_settings import RecentProjects
from src.types import Tk_Win
from src.Utils.functions import is_illegal_filename
from src.Utils.images import get_image, init_images
from src.Widgets.link import Link
from src.Widgets.tkentry import Entry
from src.Widgets.winframe import WinFrame


class NewProjectDialog(WinFrame):
    def __init__(self, master: Tk_Win, open_func: Callable):
        self.open_func = open_func
        self.master = master
        super().__init__(master, "New Project")
        self.directory_to_create = os.path.expanduser("~/")
        self.projects = RecentProjects(self.master)

        frame = ttk.Frame(self)
        ttk.Label(frame, text="Name: ").grid(row=0, column=0, sticky="e")
        self.name = Entry(frame)
        self.name.grid(row=0, column=1)
        ttk.Label(frame, text="Directory: ").grid(row=1, column=0, sticky="e")
        self.directory = Entry(frame)
        self.directory.grid(row=1, column=1)
        self.directory.insert("0", self.directory_to_create)

        self.status = ttk.Label(frame, foreground="red", takefocus=False)
        self.status.grid(row=2, column=1, sticky="w")

        self.create_btn = ttk.Button(frame, text="Create", command=self.create)
        self.create_btn.grid(row=3, column=1, sticky="e")

        frame.pack(fill="both", expand=True)

        self.name.entry.bind("<KeyRelease>", self.on_name_change)

    def create(self):
        os.mkdir(self.directory_to_create)
        self.projects.add_project(self.name.get(), self.directory_to_create)
        name = self.projects.get_name_for_path(self.directory_to_create)
        self.open_func(name)

    def on_name_change(self, _):
        directory = self.directory.get()
        name = self.name.get()
        if is_illegal_filename(name) is None:  # When the name is not recommended
            self.status["text"] = "This name is legal, though not recommended. It is considered too long"
        if is_illegal_filename(name):  # When it is illegal, should return early
            self.status["text"] = "Invalid name"
            self.create_btn["state"] = "disabled"
            return
        # Reset the status. The project name is okay
        self.create_btn["state"] = "normal"
        self.status["text"] = ""

        directory = os.path.join(directory, name)
        self.directory_to_create = directory
        self.title_text = f"New Project - {directory}"
        self.create_titlebar()


class StartDialog:
    def __init__(self, master: Tk_Win) -> None:
        init_images()
        self.master = master

        self.settings_class = GeneralSettings(self.master)
        self.style = ttkthemes.ThemedStyle(self.master)
        self.style.theme_use(self.settings_class.get_settings("ttk_theme"))
        logger.debug("Theme loaded")

        self.master.withdraw()
        self.icon = get_image("pyplus")
        self.frame = WinFrame(self.master, "Start", icon=self.icon, disable=False)
        self.frame.geometry("710x580")
        self.frame.resizable(False, False)

        self.frame.bind("<Destroy>", lambda _: sys.exit(0))

        empty_menu = tk.Menu(master)
        if OSX:
            app_menu = tk.Menu(empty_menu, name="apple")
            empty_menu.add_cascade(menu=app_menu)
        master.config(menu=empty_menu)
        self.functions = []
        self.create_links()

        self.project_view = ProjectView(self.frame, self.open_project)
        self.project_view.pack(side="bottom", fill="both", expand=True)
        self.frame.create_bar()

    def open_project(self, project):
        self.frame.withdraw()
        Editor(self.master, project)
        self.master.deiconify()

        # If project closes, show the welcome dialog
        self.master.protocol("WM_DELETE_WINDOW", lambda: self.__init__(self.master))

    def new_project(self):
        NewProjectDialog(self.master, self.open_project)

    def clone(self):
        ...

    @property
    def links(self) -> Dict[str, str]:
        with open("Config/start.json") as f:
            links = json.load(f)
        return links

    def create_links(self):
        frame = self.frame

        self.first_tab = first_tab = ttk.Frame(frame)
        frame.add_widget(first_tab)
        bold = font.Font(family="tkDefaultFont", size=35, weight="bold")
        ttk.Label(
            first_tab, text="Welcome!", font=bold, image=get_image("pyplus-35px", "image"), compound="left"
        ).pack(anchor="nw")
        links = self.links
        for text in links.keys():
            exec(f"self.functions.append(lambda _: {links[text][1]})", {"self": self, "frame": frame})
            item = Link(first_tab, text, get_image(links[text][0]), command=self.functions[-1])
            item.pack(side="left", anchor="nw")
            item.bind("<Button>", lambda _: frame.destroy(), add=True)
        logger.debug("Start screen created")
