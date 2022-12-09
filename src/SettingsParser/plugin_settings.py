import re

import json5rw as json

from src.constants import logger
from src.errors import EditorErr
from src.SettingsParser.menu import Menu

PLUGIN_MENU_PATTERN = re.compile(r"(\[(.+?)\](@(W|!W|M|!M|L|!L|A))?) -> (\[(.+?\])(@(W|!W|M|!M|L|!L|A))?)")


def parse_name(name):
    name_re = re.match(PLUGIN_MENU_PATTERN, name)
    if not name_re:
        raise EditorErr("Invalid plugin menu configuration")
    orig_menu = name_re.group(1)
    plugin_menu = name_re.group(5)

    return [orig_menu, plugin_menu]


class Plugins:
    staticmethod(parse_name)

    def __init__(self, master, menu: Menu) -> None:
        self.master = master
        self.menu = menu
        with open("Config/default/plugin-data.json") as f:
            self.settings = json.load(f)
        with open("Config/plugin-data.json") as f:
            self.settings |= json.load(f)

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
