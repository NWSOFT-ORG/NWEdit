import os
from pathlib import Path
from typing import *

import json5rw as json

from src.Components.commondialog import ErrorInfoDialog
from src.constants import logger
from src.SettingsParser.configfiles import RECENT_PROJECTS


class RecentProjects:
    def __init__(self, master):
        self.master = master
        self.config = {}
        self.reload_config()

    def create_config(self):
        with RECENT_PROJECTS.open("w") as f:
            json.dump({}, f)
        self.reload_config()

    def reload_config(self):
        try:
            with RECENT_PROJECTS.open() as f:
                self.config |= json.load(f)
        except (ValueError, FileNotFoundError):
            self.create_config()

    def get_path_to(self, name: str) -> Path:
        if not self.config:
            return Path("")
        return Path(self.config[name]["path"])

    def get_name_for_path(self, path: Path) -> str:
        if not self.config:
            return ""
        for key, value in self.config.items():
            if value["path"] == path:
                return key

    def set_open_files(self, name: str, files: Dict[Path, str]):
        if not self.config:
            return
        if not files:
            self.config[name]["openFiles"] = {}
        for file, index in files.items():
            self.config[name]["openFiles"][file.as_posix()] = index
        self.write_config()

    def get_open_files(self, name: str) -> Dict[str, str]:
        if not self.config:
            return {}
        files = self.config[name]["openFiles"]
        return files

    def get_treeview_stat(self, name: str) -> Dict[str, Union[List[str], str]]:
        if not self.config:
            return {}
        config = {}
        stats = ("expandedNodes", "yScrollbarLocation", "xScrollbarLocation")
        for item in stats:
            config[item] = self.config[name][item]
        return config

    def set_tree_status(self, name: str, status: Dict[str, str]):
        if not self.config:
            return
        if not status:
            self.config[name] = {}
        for key, value in status.items():
            self.config[name][key] = value
        self.write_config()

    def add_project(self, name: str, path: Path):
        if not self.config:
            self.config = {}
        self.config[name] = {
            "openFiles"         : {},
            "path"              : path.as_posix(),
            "expandedNodes"     : [],
            "yScrollbarLocation": [0, 0],
            "xScrollbarLocation": [0, 0],
            "icon"              : None
        }
        self.write_config()

    def remove_project(self, name: str):
        if not self.config:
            return
        self.config.pop(name)
        self.write_config()

    def assign_icon(self, name: str, icon: os.PathLike):
        if not self.config:
            return
        if os.path.isfile(icon):
            self.config[name]["icon"] = icon
            self.write_config()
        else:
            ErrorInfoDialog(self.master, "The file selected does not exist")

    def write_config(self):
        with RECENT_PROJECTS.open("w") as f:
            json.dump(self.config, f)
        logger.debug("Updated project config")
        self.reload_config()
