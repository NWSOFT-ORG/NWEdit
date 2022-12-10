import re
import sys
import tkinter as tk
from typing import Any, Dict, List, Literal, Union

import json5rw as json

from src.constants import logger, MODIFIER, OSX
from src.errors import EditorErr
from src.exceptions import ConfigurationForbiddenError
from src.Utils.images import get_image

if OSX:
    import PyTouchBar

SHIFT_PATTERN = re.compile(r"shift-([a-zA-z])")
PARENT_PATTERN = re.compile(r"\[(.+?)\](@(W|!W|M|!M|L|!L|A))?")


def convert_shift_keysym(keysym):
    res = re.search(SHIFT_PATTERN, keysym)
    if res:
        letter = res.group(1)
        keysym = re.sub(SHIFT_PATTERN, letter.upper(), keysym)
    return keysym


def compare_platforms(
    platform: Literal["win32", "darwin", "linux"],
    marker: Literal["W", "!W", "M", "!M", "L", "!L", "A", ""]
):
    if not marker or marker == "A":
        return True
    PLATFORM_IS_WINDOWS = platform == "win32"
    PLATFORM_IS_MACOS = platform == "darwin"
    PLATFORM_IS_LINUX = platform == "linux"
    PLATFORM_IS_NOT_WINDOWS = platform != "win32"
    PLATFORM_IS_NOT_MACOS = platform != "darwin"
    PLATFORM_IS_NOT_LINUX = platform != "linux"

    MARKER_IS_WINDOWS = marker == "W"
    MARKER_IS_MACOS = marker == "M"
    MARKER_IS_LINUX = marker == "L"
    MARKER_IS_NOT_WINDOWS = marker == "!W"
    MARKER_IS_NOT_MACOS = marker == "!M"
    MARKER_IS_NOT_LINUX = marker == "!L"
    return (PLATFORM_IS_WINDOWS and MARKER_IS_WINDOWS) or (PLATFORM_IS_NOT_WINDOWS and MARKER_IS_NOT_WINDOWS) or \
        (PLATFORM_IS_MACOS and MARKER_IS_MACOS) or (PLATFORM_IS_NOT_MACOS and MARKER_IS_NOT_MACOS) or \
        (PLATFORM_IS_LINUX and MARKER_IS_LINUX) or (PLATFORM_IS_NOT_LINUX and MARKER_IS_NOT_LINUX)


class MenuPlaceHolderSettings():
    """Gets the shortcuts to show in the menus"""

    def __init__(self, obj, vars_: Dict[str, Any] = {}):
        self.obj = obj
        self.vars = vars_

        with open("Config/default/menu.json") as f:
            config = json.load(f)
            if not config:
                return
            self.config: Dict[str, None] = config["@place_holders"]  # Load shortcuts only
        with open("Config/menu.json") as f:
            config = json.load(f)
            if not config:
                return
            self.config |= config["@place_holders"]  # Load shortcuts only

    def change(self, obj, vars_: Dict[str, Any] = {}):
        self.obj = obj
        self.vars = vars_

    def get_place_holder(self, name):
        try:
            command = self.config[name]
            exec(
                command, {
                    "obj": self.obj,
                    **self.vars
                }
            )
        except Exception:
            logger.exception("Cannot run place holder command")


class Menu:
    def __init__(self, obj, menu_type: str = "main", disable_on_no_tabs: bool = False):
        """A menu creater from configuration"""
        if menu_type.startswith("@"):
            raise ConfigurationForbiddenError()
        self.menu_name = menu_type
        self.disable_on_no_tabs = disable_on_no_tabs
        self.obj = obj
        self.master = obj.master
        self.menu = tk.Menu(self.master)
        self.apple = tk.Menu(self.menu, name="apple")
        self.functions = []
        self.disable_menus = {}

        self.place_holder_settings = MenuPlaceHolderSettings(None)

        with open("Config/default/menu.json") as f:
            config = json.load(f)
            if not config:
                return
            self.config: Dict[str, Union[List, Dict]] = config[self.menu_name]  # Load main menu only
        with open("Config/menu.json") as f:
            config = json.load(f)
            if not config:
                return
            self.config |= config[self.menu_name]  # Load main menu only
        self.load_config()

    def load_config(self):
        """Reloads configuration"""
        self.menu.delete(0, "end")
        self.create_menu(self.menu, self.config)

    def create_menu(self, menu, config):
        """Recursively loop through the configuration
        [x] = cascade, x = item
        Will also create bindings"""
        for key in config.keys():
            if key.startswith("@") and config[key] is None:
                self.place_holder_settings.change(obj=menu)
                self.place_holder_settings.get_place_holder(key)
            elif not re.match(PARENT_PATTERN, key):
                # Item
                cnf = {"menu": menu, "text": key, **config[key]}
                logger.debug(f"Creating item {key!r}")
                if cnf["disable"]:
                    if menu not in self.disable_menus.keys():
                        self.disable_menus[menu] = []
                    self.disable_menus[menu].append(key)
                cnf.pop("disable")
                if compare_platforms(sys.platform, cnf["platform"]):
                    cnf.pop("platform")
                    self.create_item(**cnf)
            else:
                # Parent
                cnf = {}
                logger.debug(f"Creating parent {key!r}")
                if key == "[NWEdit]@M":  # Create application menu on macOS only!
                    cnf["name"] = "apple"
                    logger.debug("Creating apple menu")
                    self.apple = tk.Menu(menu, **cnf)
                platform_re = re.findall(PARENT_PATTERN, key)
                if not platform_re:
                    logger.error("Invalid menu syntax")
                    sys.exit(1)

                platform_re = platform_re[0]
                platform = platform_re[2]
                name = platform_re[0]

                if compare_platforms(sys.platform, platform):
                    cascade = tk.Menu(menu, **cnf)
                    self.create_menu(cascade, config[key])
                    menu.add_cascade(menu=cascade, label=name)

    def disable(self, tabs):
        logger.debug(f"{bool(tabs)=!r}. Therefore, {'enable' if tabs else 'disable'} menu items")
        for key in self.disable_menus.keys():
            for value in self.disable_menus[key]:
                key.entryconfig(value, state="disabled" if not tabs else "normal")

    @staticmethod
    def do_import(name):
        """Construct an import statement with configuration"""
        imports = name.split(" -> ")
        if len(imports) == 2:
            statement = f"from {imports[0]} import {imports[1]}"
        else:
            statement = f"import {imports[0]}"
        logger.debug(f"Imported a module: {statement}")
        return statement

    def create_item(self, menu, text, icon, mnemonic, function, imports):
        local_vars = {}
        if imports:
            exec(self.do_import(imports), local_vars)  # Imports things as plugins
        exec(
            f"self.functions.append(lambda _=None: {function}\
            {'if obj.tabs else None' if self.disable_on_no_tabs else ''})",
            {"obj": self.obj, "self": self, **local_vars}
        )
        cnf = {
            "label"      : text,
            "image"      : get_image(icon),
            "accelerator": f"{MODIFIER}-{mnemonic}",
            "compound"   : "left",
            "command"    : self.functions[-1]
        }
        if not mnemonic:
            cnf.pop("accelerator")  # Will cause error with an empty accelerator
            logger.debug("No Accelerator")
        elif mnemonic:
            self.master.bind(f'<{MODIFIER}-{convert_shift_keysym(mnemonic)}>', self.functions[-1])
        elif mnemonic.startswith("`"):
            cnf["accelerator"] = mnemonic[1:]
            logger.debug("Bare Accelerator")

        menu.add_command(**cnf)


class TouchBar():
    """A TouchBar creater from configuration"""

    def __init__(self, obj, disable_on_no_tabs: bool = False):
        if not OSX:
            raise EditorErr("Use TouchBar on macOS only!")
        self.obj = obj
        self.disable_on_no_tabs = disable_on_no_tabs
        self.master = obj.master
        self.functions = []

        self.place_holder_settings = MenuPlaceHolderSettings(self)

        # Initialization
        self.load_config()
        PyTouchBar.prepare_tk_windows(self.master)

    @staticmethod
    def do_import(name):
        """Construct an import statement with configuration"""
        imports = name.split(" -> ")
        if len(imports) == 2:
            statement = f"from {imports[0]} import {imports[1]}"
        else:
            statement = f"import {imports[0]}"
        logger.debug(f"Imported a module: {statement}")
        return statement

    def load_config(self):
        with open("Config/default/menu.json") as f:
            config = json.load(f)
            if not config:
                return
            self.config: Dict[str, Union[List, Dict]] = config["touchbar"]  # Load touchbar only
        with open("Config/menu.json") as f:
            config = json.load(f)
            if not config:
                return
            self.config |= config["touchbar"]  # Load touchbar only

    def create_touchbar(self):
        items = []
        for icon in self.config.keys():
            if icon.startswith("@"):
                self.place_holder_settings.change(self, vars_={"obj": PyTouchBar, "items": items})
                self.place_holder_settings.get_place_holder(icon)
                continue
            else:
                item = self.create_item(
                    self.config[icon]["imports"], f"src/Images/{icon}.svg", self.config[icon]["function"]
                )
                items.append(item)
        PyTouchBar.set_touchbar(items)

    def create_item(self, imports, image, function):
        local_vars = {}
        if imports:
            exec(self.do_import(imports), local_vars)  # Imports things as plugins
        exec(
            f"self.functions.append(lambda _=None: {function}\
            {'if obj.tabs else None' if self.disable_on_no_tabs else ''})",
            {"obj": self.obj, "self": self, **local_vars}
        )
        item = PyTouchBar.TouchBarItems.Button(image=image, action=self.functions[-1])
        return item
