from constants import APPDIR
from dialogs import ErrorInfoDialog
from filedialog import DirectoryOpenDialog, FileOpenDialog
from modules import EditorErr, JSONLexer, Path, json, lexers, os, sys, zipfile


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


class Filetype:
    def __init__(self):
        with open(os.path.join(APPDIR, "Settings/lexer-settings.json")) as f:
            all_settings = json.load(f)
        self.extens = []
        self.lexers = []
        for key, value in all_settings.items():
            self.extens.append(key)
            self.lexers.append(value)

    def get_lexer_settings(self, extension: str):
        try:
            if lexers.get_lexer_by_name(
                self.lexers[self.extens.index(extension)]
            ) == lexers.get_lexer_by_name("JSON"):
                return JSONLexer
            return lexers.get_lexer_by_name(self.lexers[self.extens.index(extension)])
        except Exception:
            return lexers.get_lexer_by_name("Text")


class Linter:
    def __init__(self):
        with open(os.path.join(APPDIR, "Settings/linter-settings.json")) as f:
            all_settings = json.load(f)
        self.extens = []
        self.linters = []
        for key, value in all_settings.items():
            self.extens.append(key)
            self.linters.append(value)

    def get_linter_settings(self, extension: str):
        try:
            if self.linters[self.extens.index(extension)] == "none":
                return None
            return self.linters[self.extens.index(extension)]
        except ValueError:
            return None


class FormatCommand:
    def __init__(self):
        with open(os.path.join(APPDIR, "Settings/format-settings.json")) as f:
            all_settings = json.load(f)
        self.extens = []
        self.format_commands = []
        for key, value in all_settings.items():
            self.extens.append(key)
            self.format_commands.append(value)

    def get_command_settings(self, extension: str):
        try:
            if self.format_commands[self.extens.index(extension)] == "none":
                return None
            return self.format_commands[self.extens.index(extension)]
        except ValueError:
            return None


class RunCommand:
    def __init__(self):
        with open(os.path.join(APPDIR, "Settings/cmd-settings.json")) as f:
            all_settings = json.load(f)
        self.extens = []
        self.commands = []
        for key, value in all_settings.items():
            self.extens.append(key)
            self.commands.append(value)

    def get_command_settings(self, extension: str):
        try:
            if self.commands[self.extens.index(extension)] == "none":
                return None
            return self.commands[self.extens.index(extension)]
        except ValueError:
            return None


class CommentMarker:
    def __init__(self):
        with open(os.path.join(APPDIR, "Settings/comment_markers.json")) as f:
            all_settings = json.load(f)
        self.extens = []
        self.comments = []
        for key, value in all_settings.items():
            self.extens.append(key)
            self.comments.append(value)

    def get_comment_settings(self, extension: str):
        try:
            if self.comments[self.extens.index(extension)] == "none":
                return None
            return self.comments[self.extens.index(extension)]
        except ValueError:
            return None
