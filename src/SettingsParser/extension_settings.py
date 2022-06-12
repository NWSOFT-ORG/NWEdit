from typing import *

from pygments.lexer import Lexer

from src.modules import json, lexers
from src.Utils.photoimage import IconImage


class ExtensionSettings:
    """An inheratiable class"""

    def __init__(self, path: str) -> None:
        with open(path) as f:
            all_settings = json.load(f)
        self.extens = []
        self.items = []
        for key, value in all_settings.items():
            self.extens.append(key)
            self.items.append(value)

    def get_settings(self, extension) -> Union[str, None]:
        try:
            if self.items[self.extens.index(extension)] == "none":
                return None
            return self.items[self.extens.index(extension)]
        except ValueError:
            return None


class PygmentsLexer(ExtensionSettings):
    def __init__(self) -> None:
        super().__init__("Config/lexer-settings.json")

    def get_settings(self, extension: str) -> Lexer:
        try:
            return lexers.get_lexer_by_name(self.items[self.extens.index(extension)])
        except ValueError:
            return lexers.get_lexer_by_name("Text")


class Linter(ExtensionSettings):
    def __init__(self) -> None:
        super().__init__("Config/linter-settings.json")


class FormatCommand(ExtensionSettings):
    def __init__(self) -> None:
        super().__init__("Config/format-settings.json")


class RunCommand(ExtensionSettings):
    def __init__(self) -> None:
        super().__init__("Config/cmd-settings.json")


class CommentMarker(ExtensionSettings):
    def __init__(self) -> None:
        super().__init__("Config/comment-markers.json")


class FileTreeIconSettings:
    def __init__(self) -> None:
        self.path = "Config/file-icons.json"
        self.dark = False
        self.folder_icon = IconImage(file="Images/file-icons/folder.png")

    def get_icon(self, extension: str) -> IconImage:
        with open(self.path) as f:
            settings = json.load(f)
        try:
            icon_name = settings[extension]
        except KeyError:
            icon_name = "other"
        return IconImage(file=f"Images/file-icons/{icon_name}.png")
