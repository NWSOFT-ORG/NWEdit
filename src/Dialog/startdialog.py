from typing import *

from src.constants import logger
from src.editor import Editor
from src.modules import font, json, sys, tk, ttk, ttkthemes
from src.project import ProjectView
from src.SettingsParser.general_settings import GeneralSettings
from src.types import Tk_Win
from src.Utils.images import get_image, init_images
from src.Widgets.link import Link
from src.Widgets.winframe import WinFrame


class StartDialog:
    def __init__(self, master: Tk_Win) -> None:
        init_images()
        self.master = master

        self.settings_class = GeneralSettings(self.master)
        self.style = ttkthemes.ThemedStyle(self.master)
        self.style.theme_use(self.settings_class.get_settings("theme"))
        logger.debug("Theme loaded")

        self.master.withdraw()
        self.icon = get_image("pyplus")
        self.frame = WinFrame(self.master, "Start", icon=self.icon, disable=False)
        self.frame.geometry("710x580")
        self.frame.resizable(False, False)

        self.frame.bind("<Destroy>", lambda _: sys.exit(0))

        empty_menu = tk.Menu(master)
        master.config(menu=empty_menu)
        self.functions = []
        self.create_links()

        self.project_view = ProjectView(self.frame, self.open_project)
        self.project_view.pack(side="bottom", fill="both", expand=True)

    def open_project(self, project):
        self.frame.withdraw()
        Editor(self.master, project)
        self.master.deiconify()

    def new_project(self):
        ...

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
