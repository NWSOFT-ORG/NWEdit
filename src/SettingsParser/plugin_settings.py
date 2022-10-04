import json5 as json

from src.constants import logger
from src.SettingsParser.menu import Menu


def parse_name(name):
    name = name.split(" -> ")
    if len(name) < 1:
        logger.error("Plugin menu incorrect")
    for index, _ in enumerate(name):
        if not index % 2:
            name[index] += "]"
        else:
            name[index] = "[" + name[index]
    return name


class Plugins:
    staticmethod(parse_name)

    def __init__(self, master, menu: Menu) -> None:
        self.master = master
        self.menu = menu
        with open("Config/plugin-data.json") as f:
            self.settings = json.load(f)
        # self.create_tool_menu()

    def load_plugins(self) -> None:
        plugins = []
        if not self.settings:
            return
        for module in self.settings.values():
            try:
                exec(
                    f"""\
from src.{module} import Plugin
p = Plugin()
plugins.append(p.PLUGIN_DATA)
del Plugin""",
                    locals(),
                    globals(),
                )
            except ModuleNotFoundError:
                logger.exception("Error, can't parse plugin settings:")
        for plugin in plugins:
            for name, menu in plugin["menu"].items():
                master_menu, child_menu = parse_name(name)
                self.menu.config[master_menu][child_menu] = menu

        self.menu.load_config()
