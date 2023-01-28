from pathlib import Path
from typing import List

import json5rw as json

from src.constants import APPDIR
from src.SettingsParser.configfiles import DEFAULT_HELPFILES, HELPFILES


class HelpFiles():
    def __init__(self) -> None:
        with DEFAULT_HELPFILES.open() as f:
            self.helpfiles = json.load(f)
        with HELPFILES.open() as f:
            self.helpfiles |= json.load(f)

    def get_name(self) -> List[str]:
        if self.helpfiles is None:
            return []
        names: List[str] = list(self.helpfiles.keys())
        names.remove("[default]")
        return names

    def get_file(self, name) -> str:
        if self.helpfiles is None:
            raise ValueError("No help files found")
        elif name == "[defaults]":
            raise Warning("Use the get_default property instead")
        return (Path(APPDIR).parent / "docs" / self.helpfiles[name]).as_posix()

    @property
    def get_default(self) -> str:
        if self.helpfiles is None:
            raise ValueError("No help files found")
        return self.get_file("[default]")
