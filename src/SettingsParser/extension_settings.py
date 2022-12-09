import io
from typing import Union

import cairosvg
import json5rw as json
from PIL import Image, ImageTk
from pygments import lexers
from pygments.lexer import Lexer


class ExtensionSettings:
    """An inheratiable class"""

    def __init__(self, path: str) -> None:
        self.path = path
        self.extens = []
        self.items = []

        self.load_config()

    def load_config(self):
        all_settings = self.load_default_config()
        with open(f"Config/{self.path}") as f:
            all_settings |= json.load(f)

        for key, value in all_settings.items():
            self.extens.append(key)
            self.items.append(value)

    def load_default_config(self):
        with open(f"Config/default/{self.path}") as f:
            all_settings = json.load(f)
        return all_settings

    def get_settings(self, extension) -> Union[str, None]:
        try:
            if self.items[self.extens.index(extension)] == "none":
                return None
            return self.items[self.extens.index(extension)]
        except ValueError:
            return None


class PygmentsLexer(ExtensionSettings):
    def __init__(self) -> None:
        super().__init__("lexer-settings.json")

    def get_settings(self, extension: str) -> Lexer:
        try:
            return lexers.get_lexer_by_name(self.items[self.extens.index(extension)])
        except ValueError:
            return lexers.get_lexer_by_name("Text")


class Linter(ExtensionSettings):
    def __init__(self) -> None:
        super().__init__("linter-settings.json")


class FormatCommand(ExtensionSettings):
    def __init__(self) -> None:
        super().__init__("format-settings.json")


class RunCommand(ExtensionSettings):
    def __init__(self) -> None:
        super().__init__("cmd-settings.json")


class CommentMarker(ExtensionSettings):
    def __init__(self) -> None:
        super().__init__("comment-markers.json")


class FileTreeIconSettings:
    def __init__(self) -> None:
        self.path = "file-icons.json"
        self.settings = {}

        self.load_config()

    @property
    def folder_icon(self) -> ImageTk.PhotoImage:
        out = io.BytesIO()
        cairosvg.svg2png(url=f"Images/file-icons/folder.svg", write_to=out, unsafe=True, scale=5)
        img = Image.open(out)
        img = img.resize((img.width // 5, img.height // 5), 1)
        return ImageTk.PhotoImage(img)

    def load_config(self):
        with open(f"Config/default/{self.path}") as f:
            self.settings |= json.load(f)
        with open(f"Config/{self.path}") as f:
            self.settings |= json.load(f)

    def get_icon(self, extension: str) -> ImageTk.PhotoImage:
        try:
            if self.settings:
                icon_name = self.settings[extension]
            else:
                icon_name = "other"
        except KeyError:
            icon_name = "other"
        out = io.BytesIO()
        cairosvg.svg2png(url=f"Images/file-icons/{icon_name}.svg", write_to=out, unsafe=True, scale=5)
        img = Image.open(out)
        img = img.resize((img.width // 5, img.height // 5), 1)
        return ImageTk.PhotoImage(img)
