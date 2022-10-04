import re
import tkinter as tk
from typing import Union, Dict, List

import json5 as json

from src.constants import MAIN_KEY, logger
from src.Utils.images import get_image
from src.errors import EditorErr

SHIFT_PATTERN = re.compile(r"shift-([a-zA-z])")


def convert_shift_keysym(keysym):
    res = re.search(SHIFT_PATTERN, keysym)
    if res:
        letter = res.group(1)
        keysym = re.sub(SHIFT_PATTERN, letter.upper(), keysym)
    return keysym


class Menu:
    def __init__(self, obj, menu_type: str = "main", disable_tabs: bool = False):
        """A menu creater from configuration"""
        self.menu_name = menu_type
        self.disable_tabs = disable_tabs
        self.obj = obj
        self.master = obj.master
        self.menu = tk.Menu(self.master)
        self.apple = tk.Menu(self.menu, name="apple")
        self.functions = []
        self.disable_menus = {}
        with open("Config/menu.json") as f:
            config = json.load(f)
            if not config:
                raise EditorErr("Menu configuration is empty")
            self.config: Dict[str, Union[List, Dict]] = config[self.menu_name]  # Load main menu only
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
            if key == "---":
                menu.add_separator()
            elif not (key.startswith("[") and key.endswith("]")):
                cnf = [menu, key, *config[key][:-1]]
                logger.debug(f"Creating item {key!r}")
                logger.debug(f"Disable on no editors: {config[key][-1]}")
                if config[key][-1]:
                    if menu not in self.disable_menus.keys():
                        self.disable_menus[menu] = []
                    self.disable_menus[menu].append(key)
                self.create_item(*cnf)
            else:
                cnf = {}
                if key == "[PyPlus]":
                    cnf["name"] = "apple"
                    logger.debug("Creating apple menu")
                    self.apple = tk.Menu(menu, **cnf)
                cascade = tk.Menu(menu, **cnf)
                self.create_menu(cascade, config[key])
                menu.add_cascade(menu=cascade, label=key[1:-1])
        logger.debug(f"Menus disabled when no editors: {self.disable_menus!r}")

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

    def create_item(self, menu, text, image, mnemonic, function, imports):
        local_vars = {}
        if imports:
            exec(self.do_import(imports), local_vars)  # Imports things as plugins
        exec(
            f"self.functions.append(lambda _=None: {function} {'if obj.tabs else None' if self.disable_tabs else ''})",
            {"obj": self.obj, "self": self, **local_vars}
        )
        cnf = {
            "label"      : text,
            "image"      : get_image(image),
            "accelerator": f"{MAIN_KEY}-{mnemonic}",
            "compound"   : "left",
            "command"    : self.functions[-1]
        }
        if not mnemonic:
            cnf.pop("accelerator")  # Will cause error with an empty accelerator
            logger.debug("No Accelerator")
        elif mnemonic:
            self.master.bind(f'<{MAIN_KEY}-{convert_shift_keysym(mnemonic)}>', self.functions[-1])
        elif mnemonic.startswith("`"):
            cnf["accelerator"] = mnemonic[1:]
            logger.debug("Bare Accelerator")

        menu.add_command(**cnf)
