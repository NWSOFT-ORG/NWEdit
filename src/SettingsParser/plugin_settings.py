import tkinter as tk

import json5 as json

from src.constants import logger
from src.Plugins.plugins_view import PluginView


class Plugins:
    def __init__(self, master) -> None:
        self.master = master
        self.tool_menu = tk.Menu(self.master)
        with open("Config/plugin-data.json") as f:
            self.settings = json.load(f)
        self.create_tool_menu()

    def load_plugins(self) -> None:
        plugins = []
        for value in self.settings.values():
            try:
                exec(
                    f"""\
from src.{value} import Plugin
p = Plugin(self.master)
plugins.append(p.PLUGIN_DATA)
del Plugin""",
                    locals(),
                    globals(),
                )
            except ModuleNotFoundError:
                logger.exception("Error, can't parse plugin settings:")
        for plugin in plugins:
            self.tool_menu.add_cascade(label=plugin["name"], menu=plugin["menu"])

    def create_tool_menu(self):
        self.tool_menu.add_command(
            label="Manage Plugins...", command=lambda: PluginView(self.master)
        )
