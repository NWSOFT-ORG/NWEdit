from src.Dialog.commondialog import ErrorInfoDialog
from src.Dialog.filedialog import DirectoryOpenDialog, FileOpenDialog
from src.Plugins.plugins_view import PluginView
from src.constants import APPDIR, logger
from src.modules import EditorErr, Path, json, lexers, os, sys, zipfile, tk
from json import JSONDecodeError


class GeneralSettings:
    """A class to read data to/from general-settings.json"""

    def __init__(self, master: [tk.Tk, tk.Toplevel, tk.Misc, str] = "."):
        self.master = master
        try:
            with open("Config/general-settings.json") as f:
                self.settings = json.load(f)
            self.theme = self.settings["theme"]
            self.highlight_theme = self.settings["pygments"]
            self.tabwidth = self.settings["tabwidth"]
            self.font = self.settings["font"].split()[0]
            self.size = self.settings["font"].split()[1]
        except JSONDecodeError:
            ErrorInfoDialog(self.master, text="Setings are corrupted.")
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
            os.path.join(backupdir, "Config.zip"), "w", zipfile.ZIP_DEFLATED
        ) as zipobj:
            zipdir("Config/", zipobj)
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

    def unzipsettings(self, master):
        FileOpenDialog(master, self.unzip_settings)

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

    def create_menu(self, open_file, master):
        menu = tk.Menu(master)
        menu.add_command(
            label="General Settings",
            command=lambda: open_file("Config/general-settings.json"),
        )
        menu.add_command(
            label="Format Command Settings",
            command=lambda: open_file("Config/format-settings.json"),
        )
        menu.add_command(
            label="File Icon Settings",
            command=lambda: open_file("Config/file-icons.json"),
        )
        menu.add_command(
            label="Lexer Settings",
            command=lambda: open_file("Config/lexer-settings.json"),
        )
        menu.add_command(
            label="Linter Settings",
            command=lambda: open_file("Config/linter-settings.json"),
        )
        menu.add_command(
            label="Run Command Settings",
            command=lambda: open_file("Config/cmd-settings.json"),
        )
        menu.add_command(label="Backup Settings to...", command=self.zipsettings)
        menu.add_command(
            label="Load Settings from...",
            command=lambda _: self.unzipsettings(self.master),
        )
        return menu


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
        super().__init__("Config/lexer-settings.json")

    def get_settings(self, extension: str):
        try:
            return lexers.get_lexer_by_name(self.items[self.extens.index(extension)])
        except ValueError:
            return lexers.get_lexer_by_name("Text")


class Linter(ExtensionSettings):
    def __init__(self):
        super().__init__("Config/linter-settings.json")


class FormatCommand(ExtensionSettings):
    def __init__(self):
        super().__init__("Config/format-settings.json")


class RunCommand(ExtensionSettings):
    def __init__(self):
        super().__init__("Config/cmd-settings.json")


class CommentMarker(ExtensionSettings):
    def __init__(self):
        super().__init__("Config/comment-markers.json")


class Plugins:
    def __init__(self, master):
        self.master = master
        self.tool_menu = tk.Menu(self.master)
        with open("Config/plugin-data.json") as f:
            self.settings = json.load(f)

    def load_plugins(self):
        plugins = []
        for value in self.settings.values():
            try:
                exec(
                    f"""\
from src.{value} import Plugin
p = Plugin(self.master)
plugins.append(p.PLUGIN_DATA)
del Plugin""",
                    locals(),
                    globals(),
                )
            except ModuleNotFoundError:
                logger.exception("Error, can't parse plugin settings:")
        for plugin in plugins:
            self.tool_menu.add_cascade(label=plugin["name"], menu=plugin["menu"])

    @property
    def create_tool_menu(self):
        self.tool_menu.add_separator()
        self.tool_menu.add_command(
            label="Manage Plugins...", command=lambda: PluginView(self.master)
        )
        return self.tool_menu
