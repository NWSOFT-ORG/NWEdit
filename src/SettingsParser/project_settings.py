import os
from typing import *

import json5 as json

from src.constants import logger
from src.Dialog.commondialog import ErrorInfoDialog


class RecentProjects:
    def __init__(self, master):
        self.master = master
        with open("EditorStatus/recent_projects.json") as f:
            self.config = json.load(f)

    def get_path_to(self, name: str):
        return self.config[name]["path"]

    def get_name_for_path(self, path: str):
        for key, value in self.config.items():
            if value["path"] == path:
                return key

    def set_open_files(self, name: str, files: Dict[str, str]):
        for file, index in files.items():
            self.config[name]["openFiles"][file] = index
        self.write_config()

    def get_open_files(self, name: str) -> Dict[str, str]:
        files = self.config[name]["openFiles"]
        return files

    def get_treeview_stat(self, name: str) -> Dict[str, Union[List[str], str]]:
        config = {}
        stats = ("expandedNodes", "yScrollbarLocation", "xScrollbarLocation")
        for item in stats:
            config[item] = self.config[name][item]
        return config

    def set_tree_status(self, name: str, status: Dict[str, str]):
        for key, value in status.items():
            self.config[name][key] = value
        self.write_config()

    def add_project(self, name: str, path: str):
        self.config[name] = {
            "openFiles"         : {},
            "path"              : path,
            "expandedNodes"     : [],
            "yScrollbarLocation": [0, 0],
            "xScrollbarLocation": [0, 0],
            "icon"              : None
        }
        self.write_config()

    def remove_project(self, name: str):
        self.config.pop(name)
        self.write_config()

    def assign_icon(self, name: str, icon: os.PathLike):
        if os.path.isfile(icon):
            self.config[name]["icon"] = icon
            self.write_config()
        else:
            ErrorInfoDialog(self.master, "The file selected does not exist")

    def write_config(self):
        with open("EditorStatus/recent_projects.json", "w") as f:
            json.dump(self.config, f)
        logger.debug("Updated project config")
