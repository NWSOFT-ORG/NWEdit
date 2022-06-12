# coding: utf-8
"""

+ =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-= +
| editor.py -- the editor's main file                 |
| The editor                                          |
| It's extremely small! (around 80 kB)                |
| You can visit my site for more details!             |
| +----------------------------------------------+    |
| | https://ZCG-coder.github.io/NWSOFT/PyPlusWeb |    |
| +----------------------------------------------+    |
| You can also contribute it on github!               |
| Note: Some parts are adapted from stack overflow.   |
+ =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-= +
Also, it's cross-compatible!
"""

from typing import *

from src.codefunctions import CodeFunctions
from src.constants import APPDIR, MAIN_KEY, OSX, logger
from src.Dialog.autocomplete import CompleteDialog
from src.Dialog.commondialog import ErrorInfoDialog, StringInputDialog, YesNoDialog
from src.Dialog.debugdialog import ErrorReportDialog
from src.Dialog.filedialog import DirectoryOpenDialog, FileOpenDialog, FileSaveAsDialog
from src.Dialog.goto import Navigate
from src.Dialog.splash import SplashWindow
from src.Git.gitview import GitView
from src.highlighter import recolorize_line
from src.Menu.create_menu import create_menu
from src.modules import (
    Path,
    font,
    json,
    logging,
    os,
    subprocess,
    sys,
    tk,
    traceback,
    ttk,
    ttkthemes,
)
from src.SettingsParser.extension_settings import (
    CommentMarker,
    FileTreeIconSettings,
    FormatCommand,
    Linter,
    PygmentsLexer,
    RunCommand,
)
from src.SettingsParser.general_settings import GeneralSettings
from src.SettingsParser.plugin_settings import Plugins
from src.Utils.color_utils import is_dark_color, lighten_color
from src.Utils.functions import is_binary_string
from src.Utils.images import get_image, init_images
from src.Widgets.customenotebook import ClosableNotebook
from src.Widgets.hexview import HexView
from src.Widgets.link import Link
from src.Widgets.panel import CustomTabs
from src.Widgets.statusbar import Statusbar
from src.Widgets.tktext import EnhancedText, EnhancedTextFrame, TextOpts
from src.Widgets.treeview import FileTree
from src.Widgets.winframe import WinFrame

if OSX:
    from src.modules import PyTouchBar

os.chdir(APPDIR)


class Document:
    """Helper class, for the editor."""

    def __init__(
        self, frame=None, textbox=None, file_dir: str = "", istoolwin: bool = False
    ) -> None:
        self.frame = frame
        self.file_dir = file_dir
        self.textbox = textbox
        self.istoolwin = istoolwin


class Editor:
    """The editor class."""

    # noinspection PyBroadException
    def __init__(self, master: tk.Tk) -> None:
        """The editor object, the entire thing that goes in the
        window."""
        init_images()
        empty_menu = tk.Menu(master)
        master.config(menu=empty_menu)
        # Create an empty menu to prevent mess-ups
        splash = SplashWindow(master)
        splash.set_section(10)
        self.master = master

        try:
            self.settings_class = GeneralSettings(self.master)
            self.file_settings_class = PygmentsLexer()
            self.linter_settings_class = Linter()
            self.cmd_settings_class = RunCommand()
            self.format_settings_class = FormatCommand()
            self.comment_settings_class = CommentMarker()
            self.plugins_settings_class = Plugins(master)
            self.icon_settings_class = FileTreeIconSettings()

            logger.debug("Settings classes initialised")
            splash.set_progress(1)

            self.opts = TextOpts(self.master, keyaction=self.key)
            self.theme = self.settings_class.get_settings("theme")
            self.tabwidth = self.settings_class.get_settings("tab")
            logger.debug("Code settings loaded")
            splash.set_progress(2)
            self.style = ttkthemes.ThemedStyle(self.master)
            self.style.theme_use(self.settings_class.get_settings("theme"))
            logger.debug("Theme loaded")
            splash.set_progress(3)
            self.bg = self.style.lookup("TLabel", "background")
            self.fg = self.style.lookup("TLabel", "foreground")

            self.icon = get_image("pyplus")
            self.master.iconphoto(True, get_image("pyplus-35px", "image"))
            splash.set_progress(4)

            self.tabs = {}

            self.menubar = tk.Menu(self.master)
            self.panedwin = ttk.Panedwindow(self.master, orient="horizontal")
            self.panedwin.pack(fill="both", expand=1)
            self.mainframe = ttk.Frame(self.master)
            self.mainframe.pack(fill="both", expand=1)
            self.panedwin.add(self.mainframe)
            logger.debug("UI initialised")
            splash.set_progress(5)

            self.left_panel()
            self.bottom_panel()
            self.statusbar = Statusbar()
            logger.debug("Layout created")
            splash.set_progress(6)

            self.codefuncs = CodeFunctions(
                self.master, self.tabs, self.nb, self.bottom_tabs
            )

            if OSX:
                PyTouchBar.prepare_tk_windows(self.master)
                open_button = PyTouchBar.TouchBarItems.Button(
                    image="Images/open.svg", action=lambda _: self.open_file()
                )
                save_as_button = PyTouchBar.TouchBarItems.Button(
                    image="Images/save-as.svg", action=lambda _: self.save_as()
                )
                close_button = PyTouchBar.TouchBarItems.Button(
                    image="Images/close.svg", action=lambda _: self.close_tab
                )
                space = PyTouchBar.TouchBarItems.Space.Flexible()
                run_button = PyTouchBar.TouchBarItems.Button(
                    image="Images/run.svg", action=lambda _: self.codefuncs.run
                )
                PyTouchBar.set_touchbar(
                    [open_button, save_as_button, close_button, space, run_button]
                )
                logger.debug(f"{OSX = }, therefore enable TouchBar support")
            splash.set_progress(7)
            self.plugins_settings_class.load_plugins()
            logger.debug("Plugins loaded")
            splash.set_progress(8)

            create_menu(self)
            self.right_click_menu = self.opts.create_menu[1]
            logger.debug("All menus loaded.")
            splash.set_progress(9)

            self.create_bindings()
            self.reopen_files()
            self.update_title()
            splash.set_progress(10)
        except Exception:
            logger.exception("Error when initializing:")
            ErrorReportDialog(
                self.master, "Error when starting.", traceback.format_exc()
            )
            exit(1)

    def left_panel(self):
        self.left_tabs = CustomTabs(self.panedwin)
        self.filetree = FileTree(self.left_tabs, self.open_file)
        self.panedwin.insert(0, self.left_tabs)
        self.left_tabs.add(self.filetree, text="Files")

    def bottom_panel(self):
        self.bottom_panedwin = ttk.Panedwindow(self.mainframe)

        self.nb = ClosableNotebook(self.bottom_panedwin, self.close_tab)
        self.nb.event_add("<<Click>>", "<1>")
        self.nb.bind("<<Click>>", self.click_tab)

        self.nb.enable_traversal()

        self.bottom_panedwin.pack(side="bottom", fill="both", expand=1)
        self.bottom_panedwin.add(self.nb, weight=4)
        self.bottom_tabs = CustomTabs(self.bottom_panedwin)
        self.bottom_panedwin.add(self.bottom_tabs, weight=1)

    def click_tab(self, _=None):
        try:
            self.opts.set_text(self.get_text)
        except AttributeError:
            pass

    def create_bindings(self):
        # Keyboard bindings
        self.master.bind(f"<{MAIN_KEY}-w>", self.close_tab)
        self.master.bind(f"<{MAIN_KEY}-o>", lambda _: self.open_file())
        # Mouse bindings
        self.master.bind("<<MouseEvent>>", self.mouse)
        self.master.event_add("<<MouseEvent>>", "<ButtonRelease>")

        self.master.protocol(
            "WM_DELETE_WINDOW", lambda: self.exit()
        )  # When the window is closed, or quit from Mac, do exit action
        self.master.createcommand("::tk::mac::Quit", self.exit)
        logger.debug("Bindings created")

    def start_screen(self) -> None:
        frame = WinFrame(self.master, "Start", closable=False, icon=self.icon)

        first_tab = tk.Canvas(frame, background=self.bg, highlightthickness=0)
        frame.add_widget(first_tab)

        first_tab.create_image(
            20, 20, anchor="nw", image=get_image("pyplus-35px", "image")
        )
        bold = font.Font(family="tkDefaultFont", size=35, weight="bold")
        first_tab.create_text(
            80, 20, anchor="nw", text="Welcome!", font=bold, fill=self.fg
        )
        label1 = Link(
            first_tab,
            text="Open file",
            image=get_image("open"),
        )
        label2 = Link(
            first_tab,
            text="New...",
            image=get_image("new"),
        )
        label3 = Link(
            first_tab,
            text="Clone",
            image=get_image("clone"),
        )
        label4 = Link(
            first_tab,
            text="Close",
            image=get_image("close"),
        )

        links = [label1, label2, label3, label4]

        label1.bind("<Button>", lambda _: self.open_file())
        label2.bind("<Button>", lambda _: self.filetree.new_file(*self.decide_new_file))
        label4.bind("<Button>", lambda _: frame.destroy())
        label3.bind("<Button>", lambda _: self.git("clone"))

        for y_index, item in enumerate(links):
            first_tab.create_window(
                80, 100 + (y_index - 1) * 25, window=item, anchor="nw"
            )
            item.bind("<Button>", lambda _: frame.destroy(), add=True)

        logger.debug("Start screen created")

    @property
    def decide_new_file(self) -> tuple:
        """Decide where the element should go to"""
        selected = self.filetree.tree.focus()
        if not selected:
            selected = self.filetree.root_node
            isdir = True
        else:
            path = self.filetree.get_path(selected, True)
            isdir = os.path.isdir(path)
        return selected, isdir

    def create_text_widget(self, frame: ttk.Frame) -> EnhancedText:
        """Creates a text widget in a frame."""

        panedwin = ttk.Panedwindow(frame)
        panedwin.pack(fill="both", expand=1)

        textframe = EnhancedTextFrame(panedwin)
        # The one with line numbers, and a nice dark theme
        textframe.pack(fill="both", expand=1, side="right")
        panedwin.add(textframe)
        textframe.panedwin = panedwin
        textframe.set_first_line(1)

        textbox = textframe.text  # text widget
        textbox.panedwin = panedwin
        textbox.complete = CompleteDialog(textframe, textbox, self.opts)
        textbox.frame = frame  # The text will be packed into the frame.
        textbox.bind(("<Button-2>" if OSX else "<Button-3>"), self.right_click)
        textbox.bind(f"<{MAIN_KEY}-b>", self.codefuncs.run)
        textbox.bind(f"<{MAIN_KEY}-f>", self.codefuncs.search)
        textbox.bind(
            f"<{MAIN_KEY}-n>", lambda _: self.filetree.new_file(*self.decide_new_file)
        )
        textbox.bind(f"<{MAIN_KEY}-N>", lambda _: Navigate(self.get_text))
        textbox.bind(f"<{MAIN_KEY}-r>", self.reload)
        textbox.bind(f"<{MAIN_KEY}-S>", lambda _: self.save_as())
        textbox.focus_set()
        logger.debug("Textbox created")
        return textbox

    def update_title(self, _=None) -> str:
        try:
            path = self.tabs[self.nb.get_tab].file_dir
            if self.tabs[self.nb.get_tab].istoolwin:
                self.master.title("PyPlus")
                logger.debug("update_title: Finished early")
                return "break"
            if OSX:
                self.master.attributes("-titlepath", path)
            self.master.title(f"PyPlus — {path}")
        except KeyError:
            self.master.title("PyPlus")
            self.master.attributes("-titlepath", "")
        finally:
            return "break"

    def update_statusbar(self, _=None) -> str:
        try:
            if not self.tabs:
                self.statusbar.label3.config(text="")
                return "break"
            currtext = self.get_text
            index = currtext.index("insert")
            ln = index.split(".")[0]
            col = index.split(".")[1]
            self.statusbar.label3.config(text=f"Line {ln} Col {col}")
            logger.debug("update_statusbar: OK")
        except KeyError:
            self.statusbar.label3.config(text="")
            logger.exception("Error:")
        finally:
            return "break"

    def key(self, event: tk.Event = None) -> None:
        """Event when a key is pressed."""
        try:
            if event:
                if not event.char:
                    return
            currtext = self.get_text
            recolorize_line(currtext)
            currtext.edit_separator()
            currtext.see("insert")
            currtext.complete.insert_completions()
            # Auto-save
            self.save_file()
            self.update_statusbar()
            # Update statusbar and title bar
            self.update_title()
            logger.debug("update_title: OK")
        except KeyError:
            self.master.bell()
            logger.exception("Error when handling keyboard event:")

    def mouse(self, _=None) -> None:
        """The action when the mouse is clicked"""
        try:
            self.update_statusbar()
            # Update statusbar and title bar
            self.update_title()
            logger.debug("update_title: OK")
        except KeyError:
            self.master.bell()
            logger.exception("Error when handling mouse event:")

    def reopen_files(self):
        with open("EditorStatus/open_files.json") as f:
            files_list = json.load(f)
            if not files_list:
                self.start_screen()
                return
            for file, cur_pos in files_list.items():
                self.open_file(file, askhex=False)
                textbox = self.tabs[self.nb.get_tab].textbox
                textbox.mark_set("insert", cur_pos)
                textbox.see("insert")
        with open("EditorStatus/window_status.json") as f:
            geometry = json.load(f)
            geometry = geometry["windowGeometry"]
            geometry = f"{geometry[0]}x{geometry[1]}"
            self.master.geometry(geometry)
        self.update_title()
        self.update_statusbar()

    def open_hex(self, file="") -> Union[EnhancedText, None]:
        if not file:
            FileOpenDialog(self.master, self.open_hex)
            return
        file = os.path.abspath(file)
        logger.info("HexView: opened")
        viewer = ttk.Frame(self.master)
        viewer.focus_set()
        window = HexView(viewer)
        window.open(file)
        self.tabs[viewer] = Document(viewer, EnhancedText, file, istoolwin=True)
        self.nb.add(viewer, text=f"Hex -- {os.path.basename(file)}")
        self.nb.select(viewer)
        self.update_title()
        self.update_statusbar()
        return window.textbox

    def open_dir(self, directory: str = ""):
        if not directory:
            DirectoryOpenDialog(self.master, self.open_dir)
            return

        self.filetree.set_path(directory)

    def open_file(self, file: str = "", askhex: bool = True):
        """Opens a file
        If a file is not provided, a messagebox'll
        pop up to ask the user to select the path."""
        if not file:
            FileOpenDialog(self.master, self.open_file)
            return

        file = os.path.abspath(file)
        try:
            # If the file is already opened, focus the tab
            for tab in self.tabs.items():
                if file == tab[1].file_dir:
                    self.nb.select(tab[1].frame)
                    return tab[1].textbox
            # If the file is in binary, ask the user to open in Hex editor
            if is_binary_string(open(file, "rb").read()):
                if askhex:
                    dialog = YesNoDialog(self.master, "Error", "View in Hex?")
                    if dialog.result:
                        self.open_hex(file)
                    logging.info("User pressed No.")
                    return self.get_text
                self.open_hex(file)
                return self.get_text

            extens = file.split(".")[-1]
            new_tab = ttk.Frame(self.nb)
            textbox = self.create_text_widget(new_tab)
            with open(file) as f:
                # Puts the contents of the file into the text widget.
                textbox.insert("end", f.read().replace("\t", " " * self.tabwidth))
                # Inserts file content, replacing tabs with four spaces
            self.tabs[new_tab] = Document(new_tab, textbox, file)
            self.nb.add(new_tab, text=os.path.basename(file))
            self.nb.select(new_tab)

            textbox.focus_set()
            textbox.set_lexer(self.file_settings_class.get_settings(extens))
            textbox.lint_cmd = self.linter_settings_class.get_settings(extens)
            textbox.cmd = self.cmd_settings_class.get_settings(extens)
            textbox.format_command = self.format_settings_class.get_settings(extens)
            textbox.comment_marker = self.comment_settings_class.get_settings(extens)

            textbox.see("insert")
            textbox.event_generate("<<Key>>")
            textbox.focus_set()
            textbox.edit_reset()
            self.opts.set_text(textbox)
            self.mouse()
            logging.info("File opened")
            return textbox
        except Exception as e:
            name = type(e).__name__
            if name == "IsADirectoryError":
                pass
            elif name != "ValueError":
                logger.exception("Error when opening file:")
            else:
                logger.exception("Warning! Program has ValueError.")

    def save_as(self, file: str = None) -> None:
        """Save the document as a different name."""
        if self.tabs:
            if file:
                file_dir = file
            else:
                FileSaveAsDialog(self.master, self.save_as)
                return
            curr_tab = self.nb.get_tab
            if not file_dir:
                return

            self.tabs[curr_tab].file_dir = file_dir
            self.nb.tab(curr_tab, text=os.path.basename(file_dir))
            with open(file_dir, "w") as f:
                f.write(self.tabs[curr_tab].textbox.get(1.0, "end"))
            self.update_title()
            self.reload()

    def save_file(self, _=None) -> None:
        """Save an *existing* file"""
        try:
            curr_tab = self.nb.get_tab
            if not os.path.exists(self.tabs[curr_tab].file_dir):
                self.save_as()
                return
            if os.access(self.tabs[curr_tab].file_dir, os.W_OK):
                with open(self.tabs[curr_tab].file_dir, "w") as file:
                    file.write(self.tabs[curr_tab].textbox.get(1.0, "end").strip())
            else:
                ErrorInfoDialog(self.master, "File read only")
        except KeyError:
            pass

    def right_click(self, event) -> None:
        if self.tabs:
            self.right_click_menu.tk_popup(event.x_root, event.y_root)

    def close_tab(self, event=None) -> None:
        try:
            # noinspection PyGlobalUndefined
            global selected_tab
            if self.nb.index("end"):
                # Close the current tab if close is selected from the file menu, or
                # keyboard shortcut.
                if event is None or event.type == str(2):
                    selected_tab = self.nb.get_tab
                # Otherwise, close the tab based on coordinates of center-click.
                else:
                    try:
                        index = event.widget.index(f"@{event.x},{event.y}")
                        selected_tab = self.nb.nametowidget(self.nb.tabs()[index])
                    except tk.TclError:
                        return

            self.nb.forget(selected_tab)
            self.tabs.pop(selected_tab)

            if len(self.tabs) == 0:
                self.start_screen()
            self.mouse()
        except KeyError:
            pass

    def reload(self) -> None:
        if not self.tabs:
            return
        tabs = []
        curr = self.nb.index(self.nb.select())
        self.nb.select(self.nb.index("end") - 1)
        for value in self.tabs.items():
            tabs.append(value[1])
        files = []
        for tab in tabs:
            files.append(tab.file_dir)
            self.close_tab()
        for x in files:
            self.open_file(x)
        self.nb.select(curr)

    def exit(self) -> None:
        with open("EditorStatus/treeview_stat.json", "w") as f:
            self.filetree.write_status(f)
        with open("EditorStatus/open_files.json", "w") as f:
            file_list = {}

            if self.tabs:
                for tab in self.tabs.values():
                    if tab.istoolwin:
                        continue
                    cursor_pos = tab.textbox.index("insert")
                    file_list[tab.file_dir] = cursor_pos
                file_list[self.tabs[self.nb.get_tab].file_dir] = self.tabs[
                    self.nb.get_tab
                ].textbox.index(
                    "insert"
                )  # Open the current file
            json.dump(file_list, f)
        with open("EditorStatus/window_status.json", "w") as f:
            status = {}
            self.master.update()
            width = self.master.winfo_width()
            height = self.master.winfo_height()
            status["windowGeometry"] = [width, height]
            json.dump(status, f)
        logger.info("Window is destroyed")
        self.master.quit()
        sys.exit(0)

    @staticmethod
    def restart() -> None:
        os.execv(sys.executable, [__file__] + sys.argv)

    @property
    def get_text(self) -> Union[EnhancedText, None]:
        try:
            return self.tabs[self.nb.get_tab].textbox
        except KeyError:
            pass

    def git(self, action=None) -> None:
        currdir = self.filetree.path
        if action == "clone":
            dialog = StringInputDialog(self.master, "Clone", "Remote git url:")
            url = dialog.result
            if not url:
                return
            subprocess.Popen(f"git clone {url}", shell=True, cwd=currdir)
            return
        if not os.path.exists(path := os.path.join(currdir, ".git")):
            ErrorInfoDialog(self.master, f"Not a git repository: {Path(path).parent}")
            return
        elif action == "commit":
            GitView(self.bottom_tabs)
