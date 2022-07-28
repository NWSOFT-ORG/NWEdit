import io
from typing import *

import cairosvg
import json5 as json
from PIL import Image, ImageTk
from pygments import lexers
from pygments.lexer import Lexer


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

    @property
    def folder_icon(self) -> ImageTk.PhotoImage:
        out = io.BytesIO()
        cairosvg.svg2png(url=f"Images/file-icons/folder.svg", write_to=out, unsafe=True, scale=5)
        img = Image.open(out)
        img = img.resize((img.width // 5, img.height // 5), 1)
        return ImageTk.PhotoImage(img)

    def get_icon(self, extension: str) -> ImageTk.PhotoImage:
        with open(self.path) as f:
            settings = json.load(f)
        try:
            icon_name = settings[extension]
        except KeyError:
            icon_name = "other"
        out = io.BytesIO()
        cairosvg.svg2png(url=f"Images/file-icons/{icon_name}.svg", write_to=out, unsafe=True, scale=5)
        img = Image.open(out)
        img = img.resize((img.width // 5, img.height // 5), 1)
        return ImageTk.PhotoImage(img)
