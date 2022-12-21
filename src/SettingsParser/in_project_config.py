import os
from typing import Any, Dict, Literal

import json5rw as json

from src.SettingsParser.project_settings import RecentProjects
from src.Utils.functions import shell_command
from src.Utils.regex import is_braketed, replace_braketed
from src.window import get_window


class InProjectConfig:
    """Parent class to get project configurations"""

    def __init__(self, project_name):
        master = get_window
        project_settings = RecentProjects(master)
        self.path = project_settings.get_path_to(project_name)
        self.create_config(self.path)

    @staticmethod
    def create_config(dir_name):
        """Populate directory"""
        config_dir = f"{dir_name}/.NWEdit"
        if not os.path.isdir(config_dir):
            os.mkdir(config_dir)
        for item in ["Run", "Tests", "EditorStatus"]:
            item_config_dir = f"{config_dir}/{item}"
            if not os.path.isdir(item_config_dir):
                os.mkdir(item_config_dir)
            if not os.path.isfile(f"{item_config_dir}/settings.json"):
                with open(f"{item_config_dir}/settings.json", "w") as f:
                    json.dump({}, f)

    def get_settings_file(self, item: Literal["Run", "Tests", "Lint", "EditorStatus"]):
        return f"{self.path}/.NWEdit/{item}/settings.json"

    def get_settings(self, parent: Literal["Run", "Tests", "Lint", "EditorStatus"], child: str):
        file = self.get_settings_file(parent)
        with open(file) as f:
            settings = json.load(f)
        return settings[child]


class RunConfig:
    def __init__(self, project_name):
        self.config_class = InProjectConfig(project_name)

        with open("Config/project-defaults/Run/settings.json") as f:
            self.settings = json.load(f)

        with open(self.config_class.get_settings_file("Run")) as f:
            try:
                self.settings |= json.load(f)
            except ValueError:
                with open(f.name, "w") as fp:
                    json.dump(self.settings, fp)  # Ensures that the config file is up-to-date

    @property
    def configurations(self):
        return self.settings["run"].keys()

    def format_vars(self, string: str):
        variables: Dict[str, Any] = self.settings["variables"]
        for key, value in variables.items():
            string = replace_braketed(string, key, value)

        return string

    def run(self, configuration: str):
        settings = self.settings["run"][configuration]
        commands = self.settings["commands"]

        command = settings["command"]
        if is_braketed(command):
            command = commands[settings["command"][1:-1]]

        args = settings["args"]
        program_args = settings["program_args"]
        before = settings["before"]

        if before:
            self.run(before)

        full_command = f"{command} {args} {program_args}"
        pwd = self.format_vars(settings["pwd"])

        shell_command(full_command, pwd)
