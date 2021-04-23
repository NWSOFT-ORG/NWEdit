from src.constants import APPDIR
from src.dialogs import ErrorInfoDialog
from src.filedialog import DirectoryOpenDialog, FileOpenDialog
from src.modules import EditorErr, JSONLexer, Path, json, lexers, os, sys, zipfile


class Settings:
    """A class to read data to/from general-settings.json"""

    def __init__(self):
        try:
            with open(os.path.join(APPDIR, "Settings/general-settings.json")) as f:
                self.settings = json.load(f)
            self.theme = self.settings["theme"]
            self.highlight_theme = self.settings["pygments"]
            self.tabwidth = self.settings["tabwidth"]
            self.font = self.settings["font"].split()[0]
            self.size = self.settings["font"].split()[1]
            return
        except Exception:
            ErrorInfoDialog(text="Setings are corrupted.")
            sys.exit(1)

    @staticmethod
    def zip_settings(backupdir):
        def zipdir(path, zip_obj):
            for root, _, files in os.walk(path):
                for file in files:
                    zip_obj.write(
                        os.path.join(root, file),
                        os.path.relpath(os.path.join(root, file), Path(path).parent),
                    )

        with zipfile.ZipFile(
            os.path.join(backupdir, "Settings.zip"), "w", zipfile.ZIP_DEFLATED
        ) as zipobj:
            zipdir("Settings/", zipobj)
        ErrorInfoDialog(title="Done", text="Settings backed up.")

    def zipsettings(self):
        DirectoryOpenDialog(self.zip_settings)

    @staticmethod
    def unzip_settings(backupdir):
        try:
            with zipfile.ZipFile(backupdir) as zipobj:
                zipobj.extractall(path=APPDIR)
            ErrorInfoDialog(
                title="Done",
                text="Settings extracted. Please restart to apply changes.",
            )
        except (zipfile.BadZipFile, zipfile.BadZipfile, zipfile.LargeZipFile):
            pass

    def unzipsettings(self):
        FileOpenDialog(self.unzip_settings)

    def get_settings(self, setting):
        if setting == "font":
            return f"{self.font} {self.size}"
        if setting == "theme":
            return self.theme
        if setting == "tab":
            return self.tabwidth
        if setting == "pygments":
            return self.highlight_theme
        raise EditorErr("The setting is not defined")


class ExtensionSettings:
    def __init__(self, path):
        with open(path) as f:
            all_settings = json.load(f)
        self.extens = []
        self.items = []
        for key, value in all_settings.items():
            self.extens.append(key)
            self.items.append(value)

    def get_settings(self, extension):
        try:
            if self.items[self.extens.index(extension)] == "none":
                return None
            return self.items[self.extens.index(extension)]
        except ValueError:
            return None


class Lexer(ExtensionSettings):
    def __init__(self):
        super().__init__(os.path.join(APPDIR, "Settings/lexer-settings.json"))

    def get_settings(self, extension: str):
        try:
            if lexers.get_lexer_by_name(
                self.items[self.extens.index(extension)]
            ) == lexers.get_lexer_by_name("JSON"):
                return JSONLexer
            return lexers.get_lexer_by_name(self.items[self.extens.index(extension)])
        except ValueError:
            return lexers.get_lexer_by_name("Text")


class Linter(ExtensionSettings):
    def __init__(self):
        super().__init__(os.path.join(APPDIR, "Settings/linter-settings.json"))


class FormatCommand(ExtensionSettings):
    def __init__(self):
        super().__init__(os.path.join(APPDIR, "Settings/format-settings.json"))


class RunCommand(ExtensionSettings):
    def __init__(self):
        super().__init__(os.path.join(APPDIR, "Settings/cmd-settings.json"))


class CommentMarker(ExtensionSettings):
    def __init__(self):
        super().__init__(os.path.join(APPDIR, "Settings/comment-markers.json"))
