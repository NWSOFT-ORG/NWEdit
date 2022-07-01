from src.constants import MAIN_KEY
from src.modules import json, tk
from typing import *

from src.Utils.images import get_image


class Menu:
    def __init__(self, obj):
        """A menu creater from configuration"""
        self.pyplus = obj
        self.menu = tk.Menu()
        self.functions = []
        with open("Config/menu.json") as f:
            self.config: Dict[Text, Union[List, Dict]] = json.load(f)

        self.create_menu(self.menu, self.config)

    def create_menu(self, menu, config):
        """Recursively loop through the configuration"""
        for key in config.keys():
            if not (key.startswith("[") and key.endswith("]")):
                cnf = [menu, key, *config[key]]
                self.create_item(*cnf)
            else:
                cnf = {}
                if key == "[PyPlus]":
                    cnf["name"] = "apple"
                cascade = tk.Menu(menu, **cnf)
                self.create_menu(cascade, config[key])
                menu.add_cascade(menu=cascade, label=key[1:-1])

    @staticmethod
    def do_import(name):
        """Construct an import statement with configuration"""
        imports = name.split(" -> ")
        if len(imports) == 2:
            statement = f"from {imports[0]} import {imports[1]}"
        else:
            statement = f"import {imports[0]}"
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
        elif mnemonic.startswith("`"):
            cnf["accelerator"] = mnemonic[1:]

        menu.add_command(**cnf)
