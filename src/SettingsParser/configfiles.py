from pathlib import Path

from multipledispatch import dispatch

from src.constants import APPDIR, WINDOWS

# Paths to status files
STATUS_FILES = (Path(APPDIR) / "EditorStatus").resolve()
WINDOW_STATUS = (STATUS_FILES / "window_status.json").resolve()
RECENT_PROJECTS = (STATUS_FILES / "recent_projects.json").resolve()
ALL_STATUS = [STATUS_FILES, WINDOW_STATUS, RECENT_PROJECTS]

# Paths to config files
CONFIG_FILES = (Path(APPDIR) / "Config").resolve()
CMD_SETTINGS = (CONFIG_FILES / "cmd-settings.json").resolve()
COMMENT_MARKERS = (CONFIG_FILES / "comment-markers.json").resolve()
FILE_EXTENS = (CONFIG_FILES / "file-extens.json").resolve()
FILE_ICONS = (CONFIG_FILES / "file-icons.json").resolve()
FORMAT_SETTINGS = (CONFIG_FILES / "format-settings.json").resolve()
GENERAL_SETTINGS = (CONFIG_FILES / "general-settings.json").resolve()
HELPFILES = (CONFIG_FILES / "helpfiles.json").resolve()
INTERVAL_SETTINGS = (CONFIG_FILES / "interval.json").resolve()
LEXER_SETTINGS = (CONFIG_FILES / "lexer-settings.json").resolve()
LINTER_SETTINGS = (CONFIG_FILES / "linter-settings.json").resolve()
MENU = (CONFIG_FILES / "menu.json").resolve()
PLUGIN_DATA = (CONFIG_FILES / "plugin-data.json").resolve()
START = (CONFIG_FILES / "start.json").resolve()

# Path to default config files
DEFAULT_CONFIG_FILES = (CONFIG_FILES / "defaults").resolve()
DEFAULT_CMD_SETTINGS = (DEFAULT_CONFIG_FILES / "cmd-settings.json").resolve()
DEFAULT_COMMENT_MARKERS = (DEFAULT_CONFIG_FILES / "comment-markers.json").resolve()
DEFAULT_FILE_EXTENS = (DEFAULT_CONFIG_FILES / "file-extens.json").resolve()
DEFAULT_FILE_ICONS = (DEFAULT_CONFIG_FILES / "file-icons.json").resolve()
DEFAULT_FORMAT_SETTINGS = (DEFAULT_CONFIG_FILES / "format-settings.json").resolve()
DEFAULT_GENERAL_SETTINGS = (DEFAULT_CONFIG_FILES / "general-settings.json").resolve()
DEFAULT_HELPFILES = (DEFAULT_CONFIG_FILES / "helpfiles.json").resolve()
DEFAULT_INTERVAL_SETTINGS = (DEFAULT_CONFIG_FILES / "interval.json").resolve()
DEFAULT_LEXER_SETTINGS = (DEFAULT_CONFIG_FILES / "lexer-settings.json").resolve()
DEFAULT_LINTER_SETTINGS = (DEFAULT_CONFIG_FILES / "linter-settings.json").resolve()
DEFAULT_MENU = (DEFAULT_CONFIG_FILES / "menu.json").resolve()
DEFAULT_PLUGIN_DATA = (DEFAULT_CONFIG_FILES / "plugin-data.json").resolve()
DEFAULT_START = (DEFAULT_CONFIG_FILES / "start.json").resolve()

ALL_DEFAULT_CONFIG = [DEFAULT_CONFIG_FILES, DEFAULT_CMD_SETTINGS, DEFAULT_COMMENT_MARKERS, DEFAULT_FILE_EXTENS,
                      DEFAULT_FILE_ICONS, DEFAULT_FORMAT_SETTINGS, DEFAULT_GENERAL_SETTINGS, DEFAULT_HELPFILES,
                      DEFAULT_INTERVAL_SETTINGS, DEFAULT_LEXER_SETTINGS, DEFAULT_LINTER_SETTINGS, DEFAULT_MENU,
                      DEFAULT_PLUGIN_DATA, DEFAULT_START]

# Path to project default config files
PROJECT_DEFAULT_CONFIG_FILES = (CONFIG_FILES / "project-defaults").resolve()
PROJECT_DEFAULT_LINT_SETTINGS = (PROJECT_DEFAULT_CONFIG_FILES / "Lint" / "settings.json").resolve()
PROJECT_DEFAULT_RUN_SETTINGS = (PROJECT_DEFAULT_CONFIG_FILES / "Run" / "settings.json").resolve()

# Paths to project config files
TESTS_FOLDER = Path(".NWEdit", "Tests")
TESTS_FILE = TESTS_FOLDER / "tests.json"
SETTINGS_FILE = TESTS_FOLDER / "Tests", "settings.json"

# Path to resource files
FONT_FILES = (Path(APPDIR) / "Images" / "Fonts").resolve()
FILE_ICON_FILES = (Path(APPDIR) / "Images" / "file-icons").resolve()
IMAGE_FILES = Path(APPDIR, "Images").resolve()

ALL_PROJECT_DEFAULT_CONFIG = [PROJECT_DEFAULT_CONFIG_FILES, PROJECT_DEFAULT_LINT_SETTINGS, PROJECT_DEFAULT_RUN_SETTINGS]

ALL = [*ALL_STATUS, *ALL_DEFAULT_CONFIG, *ALL_PROJECT_DEFAULT_CONFIG, FONT_FILES]


@dispatch(Path)
def to_platform_specific_path(path: Path) -> Path:
    """Converts a path to a platform-specific path."""
    if WINDOWS:
        return Path(str(path).replace("/", "\\"))
    else:
        return Path(str(path).replace("\\", "/"))


@dispatch(str)
def to_platform_specific_path(path: str) -> str:
    """Converts a path to a platform-specific path."""
    if WINDOWS:
        return path.replace("/", "\\")
    else:
        return path.replace("\\", "/")


@dispatch(Path)
def config_dir_from_name(name: Path) -> Path:
    return (name / ".NWEdit").resolve()


@dispatch(str)
def config_dir_from_name(name: str) -> str:
    return Path(name, ".NWEdit").resolve().as_posix()
