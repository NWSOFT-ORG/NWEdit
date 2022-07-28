import tkinter as tk
from typing import *

import json5 as json

from src.constants import logger, MAIN_KEY
from src.Utils.images import get_image


class Menu:
    def __init__(self, obj):
        """A menu creater from configuration"""
        self.pyplus = obj
        self.master = obj.master
        self.menu = tk.Menu()
        self.functions = []
        self.disable_menus = {}
        self.load_config()

    def load_config(self):
        """Reloads configuration"""
        with open("Config/menu.json") as f:
            self.config: Dict[str, Union[List, Dict]] = json.load(f)
        self.create_menu(self.menu, self.config)

    def create_menu(self, menu, config):
        """Recursively loop through the configuration
        [x] = cascade, x = item
        Will also create bindings"""
        for key in config.keys():
            if not (key.startswith("[") and key.endswith("]")):
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
        exec(f"self.functions.append(lambda: {function})", {"pyplus": self.pyplus, "self": self} | local_vars)
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
        elif mnemonic.startswith("`"):
            cnf["accelerator"] = mnemonic[1:]
            logger.debug("Bare Accelerator")
        # self.master.bind(f'<{cnf["accelerator"]}>', self.functions[-1])

        menu.add_command(**cnf)
