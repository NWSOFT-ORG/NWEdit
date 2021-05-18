#!/usr/local/bin/python3.9
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
from src.console import Console
from src.constants import (
    APPDIR,
    LINT_BATCH,
    MAIN_KEY,
    OSX,
    RUN_BATCH,
    VERSION,
    WINDOWS,
    logger,
)
from src.customenotebook import ClosableNotebook
from src.dialogs import ErrorInfoDialog, InputStringDialog, ViewDialog, YesNoDialog
from src.filedialog import FileOpenDialog, FileSaveAsDialog
from src.functions import (
    download_file,
    is_binary_string,
    is_dark_color,
    open_system_shell,
    run_in_terminal,
)

# These modules are from the base directory
from src.Git.commitview import CommitView
from src.Git.remoteview import RemoteView
from src.goto import Navigate
from src.hexview import HexView
from src.highlighter import create_tags, recolorize
from src.menubar import Menubar, MenuItem, Menu
from src.modules import (
    EditorErr,
    Path,
    json,
    lexers,
    logging,
    os,
    subprocess,
    sys,
    tk,
    ttk,
    ttkthemes,
    webbrowser,
)
from src.search import Search
from src.settings import (
    CommentMarker,
    FormatCommand,
    Lexer,
    Linter,
    RunCommand,
    Settings,
)
from src.statusbar import Statusbar
from src.testdialog import TestDialog
from src.tktext import EnhancedTextFrame, TextOpts
from src.treeview import FileTree

if OSX:
    from src.modules import PyTouchBar

os.chdir(APPDIR)


class Document:
    """Helper class, for the editor."""

    def __init__(self, frame, textbox, file_dir) -> None:
        self.frame = frame
        self.file_dir = file_dir
        self.textbox = textbox


class Editor:
    """The editor class."""

    def __init__(self, master) -> None:
        """The editor object, the entire thing that goes in the
        window.
        Lacks these MacOS support:
        * The file selector does not work."""
        try:
            self.settings_class = Settings()
            self.file_settings_class = Lexer()
            self.linter_settings_class = Linter()
            self.cmd_settings_class = RunCommand()
            self.format_settings_class = FormatCommand()
            self.commet_settings_class = CommentMarker()
            self.theme = self.settings_class.get_settings("theme")
            self.tabwidth = self.settings_class.get_settings("tab")
            logger.debug("Settings loaded")

            self.master = master
            self.master.geometry("1200x800")
            self.style = ttkthemes.ThemedStyle(self.master)
            self.style.set_theme(self.theme)
            self.bg = self.style.lookup("TLabel", "background")
            self.fg = self.style.lookup("TLabel", "foreground")
            if is_dark_color(self.bg):
                self.close_icon = tk.PhotoImage(file="Images/close.gif")
                self.copy_icon = tk.PhotoImage(file="Images/copy-light.gif")
                self.lint_icon = tk.PhotoImage(file="Images/lint-light.gif")
                self.delete_icon = tk.PhotoImage(file="Images/delete-light.gif")
                self.indent_icon = tk.PhotoImage(file="Images/indent-light.gif")
                self.paste_icon = tk.PhotoImage(file="Images/paste-light.gif")
                self.unindent_icon = tk.PhotoImage(file="Images/unindent-light.gif")
                self.search_icon = tk.PhotoImage(file="Images/search-light.gif")
                self.pyterm_icon = tk.PhotoImage(file="Images/py-term-light.gif")
                self.term_icon = tk.PhotoImage(file="Images/term-light.gif")
                self.format_icon = tk.PhotoImage(file="Images/format-light.gif")
                self.sel_all_icon = tk.PhotoImage(file="Images/sel-all-light.gif")
            else:
                self.close_icon = tk.PhotoImage(file="Images/close-dark.gif")
                self.lint_icon = tk.PhotoImage(file="Images/lint.gif")
                self.copy_icon = tk.PhotoImage(file="Images/copy.gif")
                self.delete_icon = tk.PhotoImage(file="Images/delete.gif")
                self.indent_icon = tk.PhotoImage(file="Images/indent.gif")
                self.paste_icon = tk.PhotoImage(file="Images/paste.gif")
                self.unindent_icon = tk.PhotoImage(file="Images/unindent.gif")
                self.search_icon = tk.PhotoImage(file="Images/search.gif")
                self.pyterm_icon = tk.PhotoImage(file="Images/py-term.gif")
                self.term_icon = tk.PhotoImage(file="Images/term.gif")
                self.format_icon = tk.PhotoImage(file="Images/format.gif")
                self.sel_all_icon = tk.PhotoImage(file="Images/sel-all.gif")

            self.cut_icon = tk.PhotoImage(file="Images/cut.gif")
            self.new_icon = tk.PhotoImage(file="Images/new.gif")
            self.open_icon = tk.PhotoImage(file="Images/open-16px.gif")
            self.redo_icon = tk.PhotoImage(file="Images/redo.gif")
            self.reload_icon = tk.PhotoImage(file="Images/reload.gif")
            self.run_icon = tk.PhotoImage(file="Images/run-16px.gif")
            self.save_as_icon = tk.PhotoImage(file="Images/saveas-16px.gif")
            self.undo_icon = tk.PhotoImage(file="Images/undo.gif")
            logger.debug("Icons loaded")
            if OSX:
                PyTouchBar.prepare_tk_windows(self.master)
                open_button = PyTouchBar.TouchBarItems.Button(
                    image="Images/open.gif", action=self._open
                )
                save_as_button = PyTouchBar.TouchBarItems.Button(
                    image="Images/saveas.gif", action=self.save_as
                )
                close_button = PyTouchBar.TouchBarItems.Button(
                    image="Images/close.gif", action=self.close_tab
                )
                space = PyTouchBar.TouchBarItems.Space.Flexible()
                run_button = PyTouchBar.TouchBarItems.Button(
                    image="Images/run.gif", action=self.run
                )
                PyTouchBar.set_touchbar(
                    [open_button, save_as_button, close_button, space, run_button]
                )
            self.icon = tk.PhotoImage(file="Images/pyplus.gif")
            self.master.iconphoto(True, self.icon)
            # Base64 image, this probably decreases the repo size.
            logger.debug("Theme loaded")

            self.tabs = {}

            self.master.protocol(
                "WM_DELETE_WINDOW", lambda: self.exit(force=False)
            )  # When the window is closed, or quit from Mac, do exit action
            self.master.createcommand("::tk::mac::Quit", self.exit)

            self.menubar = Menubar(self.master)
            self.pandedwin = ttk.Panedwindow(self.master, orient="horizontal")
            self.pandedwin.pack(fill="both", expand=1)
            frame = ttk.Frame(self.master)
            frame.pack(fill='both', expand=1)
            self.nb = ClosableNotebook(frame, self.close_tab)
            self.nb.bind("<B1-Motion>", self.move_tab)
            self.nb.pack(expand=1, fill="both")
            self.filetree = FileTree(self.master, self.open_file)
            self.pandedwin.add(self.filetree)
            self.pandedwin.add(frame)
            self.nb.enable_traversal()
            self.statusbar = Statusbar()

            self.create_menu()

            self.right_click_menu = Menu(self.master)
            self.right_click_menu.add_command(label="Undo", command=self.undo)
            self.right_click_menu.add_command(label="Redo", command=self.redo)
            self.right_click_menu.add_command(label="Cut", command=self.cut)
            self.right_click_menu.add_command(label="Copy", command=self.copy)
            self.right_click_menu.add_command(label="Paste", command=self.paste)
            self.right_click_menu.add_command(label="Delete", command=self.delete)
            self.right_click_menu.add_command(
                label="Select All", command=self.select_all
            )
            logger.debug("Right-click menu created")

            # Keyboard bindings
            self.master.bind(f"<{MAIN_KEY}-w>", self.close_tab)
            self.master.bind(f"<{MAIN_KEY}-o>", self._open)
            logger.debug("Bindings created")

            self.master.bind("<<MouseEvent>>", self.mouse)
            self.master.event_add("<<MouseEvent>>", "<ButtonRelease>")
            self.master.focus_force()
            self.update_title()
            self.update_statusbar()
            with open("Backups/recent_files.txt") as f:
                for line in f.read().split("\n"):
                    if line:
                        self.open_file(line, askhex=False)
                if not f.read():
                    self.start_screen()
            with open("Backups/recent_dir.txt") as f:
                self.filetree.path = f.read()
                self.filetree.init_ui()
        except FileNotFoundError:
            logger.exception("Error when initializing:")
            self.restart()

    def create_menu(self) -> None:
        self.appmenu = MenuItem()

        self.appmenu.add_command(label="About PyPlus", command=self._version)
        self.appmenu.add_command(
            label="General Settings",
            command=lambda: self.open_file(
                APPDIR + "/Settings/general-settings" ".json"
            ),
        )
        self.appmenu.add_command(
            label="Format Command Settings",
            command=lambda: self.open_file(
                APPDIR + "/Settings/format-settings" ".json"
            ),
        )
        self.appmenu.add_command(
            label="Lexer Settings",
            command=lambda: self.open_file(APPDIR + "/Settings/lexer-settings" ".json"),
        )
        self.appmenu.add_command(
            label="Linter Settings",
            command=lambda: self.open_file(
                APPDIR + "/Settings/linter-settings" ".json"
            ),
        )
        self.appmenu.add_command(
            label="Run Command Settings",
            command=lambda: self.open_file(APPDIR + "/Settings/cmd-settings" ".json"),
        )
        self.appmenu.add_command(
            label="Backup Settings to...", command=self.settings_class.zipsettings
        )
        self.appmenu.add_command(
            label="Load Settings from...", command=self.settings_class.unzipsettings
        )
        self.appmenu.add_command(label="Exit Editor", command=self.exit)
        self.appmenu.add_command(label="Restart app", command=self.restart)
        self.appmenu.add_command(label="Check for updates", command=self.check_updates)

        self.filemenu = MenuItem()
        self.filemenu.add_command(
            label="New...",
            command=self.filetree.new_file,
            image=self.new_icon,
        )
        self.filemenu.add_command(
            label="Open File",
            command=self._open,
            image=self.open_icon,
        )
        self.filemenu.add_command(
            label="Open File in Hex",
            command=self.openhex,
            image=self.open_icon,
        )
        self.filemenu.add_command(
            label="Save Copy to...",
            command=self._saveas,
            image=self.save_as_icon,
        )
        self.filemenu.add_command(
            label="Close Tab",
            command=self.close_tab,
            image=self.close_icon,
        )
        self.filemenu.add_command(
            label="Reload all files from disk",
            command=self.reload,
            image=self.reload_icon,
        )

        self.editmenu = MenuItem()
        self.editmenu.add_command(
            label="Undo",
            command=self.undo,
            image=self.undo_icon,
        )
        self.editmenu.add_command(
            label="Redo",
            command=self.redo,
            image=self.redo_icon,
        )
        self.editmenu.add_command(
            label="Cut",
            command=self.cut,
            image=self.cut_icon,
        )
        self.editmenu.add_command(
            label="Copy",
            command=self.copy,
            image=self.copy_icon,
        )
        self.editmenu.add_command(
            label="Paste",
            command=self.paste,
            image=self.paste_icon,
        )
        self.editmenu.add_command(
            label="Delete Selected",
            image=self.delete_icon,
            command=self.delete,
        )
        self.editmenu.add_command(
            label="Duplicate Line or Selected", command=self.duplicate_line
        )
        self.editmenu.add_command(label="Join lines", command=self.join_lines)
        self.editmenu.add_command(label="Swap case", command=self.swap_case)
        self.editmenu.add_command(label="Upper case", command=self.upper_case)
        self.editmenu.add_command(label="Lower case", command=self.lower_case)
        self.editmenu.add_command(
            label="Select All",
            command=self.select_all,
            image=self.sel_all_icon,
        )
        self.editmenu.add_command(label="Select Line", command=self.sel_line)
        self.editmenu.add_command(label="Select Word", command=self.sel_word)
        self.editmenu.add_command(label="Select Prev Word", command=self.sel_word_left)
        self.editmenu.add_command(label="Select Next Word", command=self.sel_word_right)
        self.editmenu.add_command(label="Delete Word", command=self.del_word)
        self.editmenu.add_command(label="Delete Prev Word", command=self.del_word_left)
        self.editmenu.add_command(label="Delete Next Word", command=self.del_word_right)
        self.editmenu.add_command(label="Move line up", command=self.mv_line_up)
        self.editmenu.add_command(label="Move line down", command=self.mv_line_dn)

        self.codemenu = MenuItem()
        self.codemenu.add_command(
            label="Indent",
            command=lambda: self.indent("indent"),
            image=self.indent_icon,
        )
        self.codemenu.add_command(
            label="Unident",
            command=lambda: self.indent("unindent"),
            image=self.unindent_icon,
        )
        self.codemenu.add_command(
            label="Comment/Uncomment Line or Selected", command=self.comment_lines
        )
        self.codemenu.add_command(
            label="Run",
            command=self.run,
            image=self.run_icon,
        )
        self.codemenu.add_command(
            label="Lint",
            command=self.lint_source,
            image=self.lint_icon,
        )
        self.codemenu.add_command(
            label="Auto-format",
            command=self.autopep,
            image=self.format_icon,
        )
        self.codemenu.add_command(
            label="Find and replace",
            command=self.search,
            image=self.search_icon,
        )
        self.codemenu.add_command(label="Bigger view", command=self.biggerview)
        self.codemenu.add_command(
            label="Open Python Shell",
            command=self.python_shell,
            image=self.pyterm_icon,
        )
        self.codemenu.add_command(
            label="Open System Shell",
            command=self.system_shell,
            image=self.term_icon,
        )
        self.codemenu.add_command(
            label="Unit tests",
            command=self.test,
        )

        self.navmenu = MenuItem()
        self.navmenu.add_command(label="Go to ...", command=self.goto)
        self.navmenu.add_command(label="-1 char", command=self.nav_1cb)
        self.navmenu.add_command(label="+1 char", command=self.nav_1cf)
        self.navmenu.add_command(label="Word end", command=self.nav_wordend)
        self.navmenu.add_command(label="Word start", command=self.nav_wordstart)
        self.navmenu.add_command(
            label="Classes and functions",
            command=self.view,
        )

        self.gitmenu = MenuItem()
        self.gitmenu.add_command(label="Initialize", command=lambda: self.git("init"))
        self.gitmenu.add_command(label="Commit", command=lambda: self.git("commit"))
        self.gitmenu.add_command(label="Remote", command=lambda: self.git("remote"))
        self.gitmenu.add_command(label="Clone", command=lambda: self.git("clone"))

        self.menubar.add_cascade(label="PyPlus", menu=self.appmenu)  # App menu
        self.menubar.add_cascade(label="File", menu=self.filemenu)
        self.menubar.add_cascade(label="Edit", menu=self.editmenu)
        self.menubar.add_cascade(label="Code", menu=self.codemenu)
        self.menubar.add_cascade(label="Navigate", menu=self.navmenu)
        self.menubar.add_cascade(label="Git", menu=self.gitmenu)
        if OSX:
            menu = tk.Menu(self.master)
            self.master.config(menu=menu)
        logger.debug("Menu created")

    def start_screen(self) -> None:
        first_tab = tk.Canvas(self.nb, background=self.bg, highlightthickness=0)
        first_tab.create_image(20, 20, anchor="nw", image=self.icon)
        fg = "#8dd9f7" if is_dark_color(self.bg) else "blue"
        first_tab.create_text(
            60,
            10,
            anchor="nw",
            text="Welcome to PyPlus!",
            font="Arial 50",
            fill=self.fg,
        )
        label1 = ttk.Label(
            first_tab,
            text="Open file",
            foreground=fg,
            background=self.bg,
            cursor="hand2",
            compound="left",
            image=self.open_icon,
        )
        label2 = ttk.Label(
            first_tab,
            text="New...",
            foreground=fg,
            background=self.bg,
            cursor="hand2",
            compound="left",
            image=self.new_icon,
        )
        label3 = ttk.Label(
            first_tab,
            text="Clone",
            foreground=fg,
            background=self.bg,
            cursor="hand2",
        )
        label4 = ttk.Label(
            first_tab,
            text="Exit",
            foreground=fg,
            background=self.bg,
            cursor="hand2",
            compound="left",
            image=self.close_icon,
        )
        label1.bind("<Button>", self._open)
        label2.bind("<Button>", self.filetree.new_file)
        label4.bind("<Button>", lambda _=None: self.exit(force=True))
        label3.bind("<Button>", lambda _=None: self.git("clone"))

        first_tab.create_window(50, 100, window=label1, anchor="nw")
        first_tab.create_window(50, 140, window=label2, anchor="nw")
        first_tab.create_window(50, 180, window=label3, anchor="nw")
        first_tab.create_window(50, 220, window=label4, anchor="nw")
        self.nb.add(first_tab, text="Start")
        logger.debug("Start screen created")

    def create_text_widget(self, frame: ttk.Frame) -> EnhancedTextFrame:
        """Creates a text widget in a frame."""

        panedwin = ttk.Panedwindow(frame)
        panedwin.pack(fill="both", expand=1)

        textframe = EnhancedTextFrame(panedwin)
        # The one with line numbers and a nice dark theme
        textframe.pack(fill="both", expand=1, side="right")
        panedwin.add(textframe)
        textframe.panedwin = panedwin
        textframe.set_first_line(1)

        textbox = textframe.text  # text widget
        textbox.frame = frame  # The text will be packed into the frame.
        textbox.bind(("<Button-2>" if OSX else "<Button-3>"), self.right_click)
        textbox.bind(f"<{MAIN_KEY}-b>", self.run)
        textbox.bind(f"<{MAIN_KEY}-f>", self.search)
        textbox.bind(f"<{MAIN_KEY}-n>", self.filetree.new_file)
        textbox.bind(f"<{MAIN_KEY}-N>", self.goto)
        textbox.bind(f"<{MAIN_KEY}-r>", self.reload)
        textbox.bind(f"<{MAIN_KEY}-S>", self._saveas)
        textbox.focus_set()
        create_tags(textbox)
        logger.debug("Textbox created")
        return textbox

    def undo(self):
        if not self.tabs:
            return
        self.tabs[self.get_tab()].textbox.opts.undo()

    def redo(self):
        if not self.tabs:
            return
        self.tabs[self.get_tab()].textbox.opts.redo()

    def duplicate_line(self):
        if not self.tabs:
            return
        self.tabs[self.get_tab()].textbox.opts.duplicate()

    def update_title(self, _=None) -> str:
        try:
            if not self.tabs:
                self.master.title("PyPlus -- No file open")
                logger.debug("update_title: No file open")
                return "break"
            self.master.title(f"PyPlus -- {self.tabs[self.get_tab()].file_dir}")
            logger.debug("update_title: OK")
            return "break"
        except Exception:
            self.master.title("PyPlus")
            return "break"

    def update_statusbar(self, _=None) -> str:
        try:
            if not self.tabs:
                self.statusbar.label2.config(text="No file open")
                self.statusbar.label3.config(text="")
                logger.debug("update_statusbar: No file open")
                return "break"
            currtext = self.tabs[self.get_tab()].textbox
            index = currtext.index("insert")
            ln = index.split(".")[0]
            col = index.split(".")[1]
            self.statusbar.label2.config(text=f"{self.tabs[self.get_tab()].file_dir}")
            self.statusbar.label3.config(text=f"Line {ln} Col {col}")
            logger.debug("update_statusbar: OK")
            return "break"
        except Exception:
            return "break"

    def key(self, _=None) -> None:
        """Event when a key is pressed."""
        try:
            currtext = self.tabs[self.get_tab()].textbox
            recolorize(currtext)
            currtext.edit_separator()
            currtext.see("insert")
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
        """The action done when the mouse is clicked"""
        try:
            self.update_statusbar()
            # Update statusbar and title bar
            self.update_title()
            logger.debug("update_title: OK")
        except KeyError:
            self.master.bell()
            logger.exception("Error when handling mouse event:")

    def open_hex(self, file=""):
        if file:
            file_dir = file
        else:
            file_dir = ""
            FileOpenDialog(self.open_hex)
        if file_dir:
            logger.info("HexView: opened")
            viewer = ttk.Frame(self.master)
            viewer.focus_set()
            window = HexView(viewer)
            window.open(file_dir)
            self.tabs[viewer] = Document(viewer, window.textbox, file_dir)
            self.nb.add(viewer, text=f"Hex -- {os.path.basename(file_dir)}")
            self.nb.select(viewer)
            self.update_title()
            self.update_statusbar()

    def openhex(self):
        self.open_hex()

    def open_file(self, file: str = "", askhex: bool = True) -> None:
        """Opens a file
        If a file is not provided, a messagebox'll
        pop up to ask the user to select the path."""
        if file:
            file_dir = file
        else:
            file_dir = ""
            FileOpenDialog(self.open_file)

        if file_dir:
            try:  # If the file is in binary, ask the user to open in Hex editor
                for tab in self.tabs.items():
                    if file_dir == tab[1].file_dir:
                        self.nb.select(tab[1].frame)
                        return
                if is_binary_string(open(file_dir, "rb").read()):
                    if askhex:
                        dialog = YesNoDialog(self.master, "Error", "View in Hex?")
                        if dialog.result:
                            self.open_hex(file_dir)
                        logging.info("User pressed No.")
                        return
                    self.open_hex(file_dir)
                    return

                file = open(file_dir)
                extens = file_dir.split(".")[-1]

                new_tab = ttk.Frame(self.nb)
                textbox = self.create_text_widget(new_tab)
                self.tabs[new_tab] = Document(new_tab, textbox, file_dir)
                self.nb.add(new_tab, text=os.path.basename(file_dir))
                self.nb.select(new_tab)

                # Puts the contents of the file into the text widget.
                currtext = self.tabs[new_tab].textbox
                currtext.insert("end", file.read().replace("\t", " " * self.tabwidth))
                # Inserts file content, replacing tabs with four spaces
                currtext.focus_set()
                currtext.set_lexer(self.file_settings_class.get_settings(extens))
                currtext.lint_cmd = self.linter_settings_class.get_settings(extens)
                currtext.cmd = self.cmd_settings_class.get_settings(extens)
                currtext.format_command = self.format_settings_class.get_settings(
                    extens
                )
                currtext.comment_marker = self.commet_settings_class.get_settings(
                    extens
                )

                currtext.see("insert")
                currtext.event_generate("<<Key>>")
                currtext.focus_set()
                TextOpts(currtext, bindkey=False, keyaction=self.key)
                logging.info("File opened")
                return
            except Exception as e:
                if type(e).__name__ != "ValueError":
                    logger.exception("Error when opening file:")
                else:
                    logger.exception("Warning! Program has ValueError.")

    def _open(self, _=None) -> None:
        """Prompt the user to open a file when C-O is pressed"""
        self.open_file()

    def search(self, _=None) -> None:
        Search(self.master, self.tabs[self.get_tab()].textbox)

    def save_as(self, file: str = None) -> None:
        """Save the document as a different name."""
        if self.tabs:
            if file:
                file_dir = file
            else:
                FileSaveAsDialog(self.save_as)
                return
            curr_tab = self.get_tab()
            if not file_dir:
                return

            self.tabs[curr_tab].file_dir = file_dir
            self.nb.tab(curr_tab, text=os.path.basename(file_dir))
            with open(file_dir, "w") as f:
                f.write(self.tabs[curr_tab].textbox.get(1.0, "end"))
            self.update_title()
            self.reload()

    def _saveas(self, _=None):
        self.save_as()

    def save_file(self, _=None) -> None:
        """Save an *existing* file"""
        try:
            curr_tab = self.get_tab()
            if not os.path.exists(self.tabs[curr_tab].file_dir):
                self.save_as()
                return
            if os.access(self.tabs[curr_tab].file_dir, os.W_OK):
                with open(self.tabs[curr_tab].file_dir, "w") as file:
                    file.write(self.tabs[curr_tab].textbox.get(1.0, "end").strip())
            else:
                ErrorInfoDialog(self.master, "File read only")
        except Exception:
            pass

    def copy(self) -> None:
        try:
            sel = self.tabs[self.get_tab()].textbox.get(tk.SEL_FIRST, tk.SEL_LAST)
            self.tabs[self.get_tab()].textbox.clipboard_clear()
            self.tabs[self.get_tab()].textbox.clipboard_append(sel)
        except Exception:
            pass

    def delete(self) -> None:
        self.tabs[self.get_tab()].textbox.delete(tk.SEL_FIRST, tk.SEL_LAST)
        self.key()

    def cut(self) -> None:
        try:
            currtext = self.tabs[self.get_tab()].textbox
            sel = currtext.get(tk.SEL_FIRST, tk.SEL_LAST)
            currtext.clipboard_clear()
            currtext.clipboard_append(sel)
            currtext.delete(tk.SEL_FIRST, tk.SEL_LAST)
            self.key()
        except tk.TclError:
            pass

    def paste(self) -> None:
        try:
            clipboard = self.tabs[self.get_tab()].textbox.clipboard_get()
            if clipboard:
                self.tabs[self.get_tab()].textbox.insert(
                    "insert", clipboard.replace("\t", " " * self.tabwidth)
                )
            self.key()
        except Exception:
            pass

    def select_all(self) -> None:
        try:
            curr_tab = self.get_tab()
            self.tabs[curr_tab].textbox.tag_add(tk.SEL, "1.0", tk.END)
            self.tabs[curr_tab].textbox.mark_set("insert", "end")
            self.tabs[curr_tab].textbox.see("insert")
        except Exception:
            pass

    def run(self, _=None) -> None:
        """Runs the file
        Steps:
        1) Writes run code into the batch file.
        2) Linux only: uses chmod to make the sh execuable
        3) Runs the run file"""
        try:
            if WINDOWS:  # Windows
                with open(APPDIR + "/run.bat", "w") as f:
                    f.write(
                        (
                            RUN_BATCH.format(
                                dir=APPDIR,
                                file=self.tabs[self.get_tab()].file_dir,
                                cmd=self.tabs[self.get_tab()].textbox.cmd,
                            )
                        )
                    )
                run_in_terminal("run.bat && del run.bat && exit", cwd=APPDIR)
            else:  # Others
                with open(APPDIR + "/run.sh", "w") as f:
                    f.write(
                        (
                            RUN_BATCH.format(
                                dir=APPDIR,
                                file=self.tabs[self.get_tab()].file_dir,
                                cmd=self.tabs[self.get_tab()].textbox.cmd,
                                script_dir=Path(
                                    self.tabs[self.get_tab()].file_dir
                                ).parent,
                            )
                        )
                    )
                run_in_terminal("chmod 700 run.sh && ./run.sh && rm run.sh", cwd=APPDIR)
        except Exception:
            ErrorInfoDialog(self.master, "This language is not supported.")

    @staticmethod
    def system_shell() -> None:
        open_system_shell()

    def python_shell(self) -> None:
        shell_frame = tk.Toplevel(self.master)
        ttkthemes.ThemedStyle(shell_frame).set_theme(self.theme)
        main_window = Console(shell_frame, None, shell_frame.destroy)
        main_window.text.lexer = lexers.get_lexer_by_name("pycon")
        main_window.text.focus_set()
        create_tags(main_window.text)
        recolorize(main_window.text)
        main_window.text.bind(
            "<KeyRelease>", lambda _=None: recolorize(main_window.text)
        )
        main_window.pack(fill="both", expand=1)
        shell_frame.mainloop()

    def view(self):
        if not self.tabs:
            return
        file_dir = self.tabs[self.get_tab()].file_dir
        text = self.tabs[self.get_tab()].textbox
        ViewDialog(self.master, f"Classes and functions for {file_dir}", text, file_dir)

    def right_click(self, event: tk.EventType) -> None:
        self.right_click_menu.tk_popup(event.x_root, event.y_root)

    def close_tab(self, event=None) -> None:
        global selected_tab
        try:
            if self.nb.index("end"):
                # Close the current tab if close is selected from file menu, or
                # keyboard shortcut.
                if event is None or event.type == str(2):
                    selected_tab = self.get_tab()
                # Otherwise close the tab based on coordinates of center-click.
                else:
                    try:
                        index = event.widget.index("@%d,%d" % (event.x, event.y))
                        selected_tab = self.nb.nametowidget(self.nb.tabs()[index])
                    except tk.TclError:
                        return

            self.nb.forget(selected_tab)
            self.tabs.pop(selected_tab)
            self.mouse()
        except Exception:
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

    def exit(self, force=False) -> None:
        if not force:
            with open("Backups/recent_dir.txt", "w") as f:
                f.write(self.filetree.path)
            with open("Backups/recent_files.txt", "w") as f:
                file_list = ""
                for tab in self.tabs.values():
                    file_list += tab.file_dir + "\n"
                f.write(file_list)
            self.master.destroy()
            logger.info("Window is destroyed")
        else:
            sys.exit(0)

    def restart(self) -> None:
        self.exit(force=False)
        newtk = tk.Tk()
        self.__init__(newtk)
        newtk.mainloop()

    def get_tab(self):
        return self.nb.nametowidget(self.nb.select())

    def move_tab(self, event: tk.EventType) -> None:
        if self.nb.index("end") > 1:
            y = self.get_tab().winfo_y() - 5

            try:
                self.nb.insert(
                    event.widget.index("@%d,%d" % (event.x, y)), self.nb.select()
                )
            except tk.TclError:
                return

    def _version(self) -> None:
        """Shows the version and related info of the editor."""
        ver = tk.Toplevel()
        ver.resizable(0, 0)
        ver.title("About PyPlus")
        ttk.Label(ver, image=self.icon).pack(fill="both")
        ttk.Label(ver, text=f"Version {VERSION}", font="Arial 30 bold").pack(
            fill="both"
        )
        if self.check_updates(popup=False)[0]:
            update = ttk.Label(
                ver, text="Updates available", foreground="blue", cursor="hand2"
            )
            update.pack(fill="both")
            update.bind(
                "<Button-1>",
                lambda e: webbrowser.open_new_tab(self.check_updates(popup=False)[1]),
            )
        else:
            ttk.Label(ver, text="No updates available").pack(fill="both")
        ver.mainloop()

    def lint_source(self) -> None:
        if not self.tabs:
            return
        try:
            if self.tabs[self.get_tab()].textbox.lint_cmd:
                currdir = self.tabs[self.get_tab()].file_dir
                if WINDOWS:
                    with open("lint.bat", "w") as f:
                        f.write(
                            LINT_BATCH.format(
                                cmd=self.tabs[self.get_tab()].textbox.lint_cmd
                            )
                        )
                    subprocess.call(f'lint.bat "{currdir}"', shell=True)
                    os.remove("lint.bat")
                else:
                    with open("lint.sh", "w") as f:
                        f.write(
                            LINT_BATCH.format(
                                cmd=self.tabs[self.get_tab()].textbox.lint_cmd
                            )
                        )
                    subprocess.call(
                        f'chmod 700 lint.sh && ./lint.sh "{currdir}"', shell=True
                    )
                    os.remove("lint.sh")
                self.open_file("results.txt")
                os.remove("results.txt")
        except Exception:
            ErrorInfoDialog(self.master, "This language is not supported")
            return

    def autopep(self) -> None:
        """Auto Pretty-Format the document"""
        try:
            currtext = self.tabs[self.get_tab()].textbox
            currdir = self.tabs[self.get_tab()].file_dir
            if currtext.format_command:
                subprocess.Popen(
                    f'{currtext.format_command} "{currdir}" > {os.devnull}', shell=True
                )  # Throw the autopep8 results into the bit bin.(/dev/null)
            else:
                ErrorInfoDialog(self.master, "Language not supported.")
                return
            self.reload()
        except Exception:
            logger.exception("Error when formatting:")

    def goto(self, _=None) -> None:
        if not self.tabs:
            return
        Navigate(self.tabs[self.get_tab()].textbox)

    def nav_1cf(self) -> None:
        if not self.tabs:
            return
        currtext = self.tabs[self.get_tab()].textbox
        currtext.mark_set("insert", "insert +1c")

    def nav_1cb(self) -> None:
        if not self.tabs:
            return
        currtext = self.tabs[self.get_tab()].textbox
        currtext.mark_set("insert", "insert -1c")

    def nav_wordstart(self) -> None:
        if not self.tabs:
            return
        currtext = self.tabs[self.get_tab()].textbox
        currtext.mark_set("insert", "insert -1c wordstart")

    def nav_wordend(self) -> None:
        if not self.tabs:
            return
        currtext = self.tabs[self.get_tab()].textbox
        currtext.mark_set("insert", "insert wordend")

    def sel_word(self) -> None:
        if not self.tabs:
            return
        currtext = self.tabs[self.get_tab()].textbox
        currtext.tag_remove("sel", "1.0", "end")
        currtext.tag_add("sel", "insert -1c wordstart", "insert wordend")

    def sel_word_left(self) -> None:
        if not self.tabs:
            return
        currtext = self.tabs[self.get_tab()].textbox
        currtext.mark_set("insert", "insert wordstart -2c")
        self.sel_word()

    def sel_word_right(self) -> None:
        if not self.tabs:
            return
        currtext = self.tabs[self.get_tab()].textbox
        currtext.mark_set("insert", "insert wordend +2c")
        self.sel_word()

    def sel_line(self) -> None:
        if not self.tabs:
            return
        currtext = self.tabs[self.get_tab()].textbox
        currtext.tag_add("sel", "insert linestart", "insert +1l linestart")

    def del_word(self) -> None:
        if not self.tabs:
            return
        currtext = self.tabs[self.get_tab()].textbox
        currtext.delete("insert -1c wordstart", "insert wordend")
        self.key()

    def del_word_left(self) -> None:
        if not self.tabs:
            return
        currtext = self.tabs[self.get_tab()].textbox
        currtext.mark_set("insert", "insert wordstart -2c")
        self.del_word()

    def del_word_right(self) -> None:
        if not self.tabs:
            return
        currtext = self.tabs[self.get_tab()].textbox
        currtext.mark_set("insert", "insert wordend +2c")
        self.del_word()

    def join_lines(self) -> None:
        if not self.tabs:
            return
        currtext = self.tabs[self.get_tab()].textbox
        if not currtext.tag_ranges("sel"):
            return
        sel = currtext.get("sel.first", "sel.last").splitlines()
        if len(sel) < 2:
            return
        sel = "".join(sel)
        currtext.delete("sel.first", "sel.last")
        currtext.insert("insert", sel)
        self.key()

    def mv_line_up(self) -> None:
        if not self.tabs:
            return
        currtext = self.tabs[self.get_tab()].textbox
        text = currtext.get("insert -1l lineend", "insert lineend")
        currtext.delete("insert -1l lineend", "insert lineend")
        currtext.mark_set("insert", "insert -1l")
        currtext.insert("insert", text)

    def mv_line_dn(self) -> None:
        if not self.tabs:
            return
        currtext = self.tabs[self.get_tab()].textbox
        text = currtext.get("insert -1l lineend", "insert lineend")
        currtext.delete("insert -1l lineend", "insert lineend")
        currtext.mark_set("insert", "insert +1l")
        currtext.insert("insert", text)

    def swap_case(self):
        if not self.tabs:
            return
        currtext = self.tabs[self.get_tab()].textbox
        if not currtext.tag_ranges("sel"):
            return
        text = currtext.get("sel.first", "sel.last")
        currtext.delete("sel.first", "sel.last")
        text = text.swapcase()
        currtext.insert("insert", text)
        self.key()

    def upper_case(self):
        if not self.tabs:
            return
        currtext = self.tabs[self.get_tab()].textbox
        if not currtext.tag_ranges("sel"):
            return
        text = currtext.get("sel.first", "sel.last")
        currtext.delete("sel.first", "sel.last")
        text = text.upper()
        currtext.insert("insert", text)
        self.key()

    def lower_case(self):
        if not self.tabs:
            return
        currtext = self.tabs[self.get_tab()].textbox
        if not currtext.tag_ranges("sel"):
            return
        text = currtext.get("sel.first", "sel.last")
        currtext.delete("sel.first", "sel.last")
        text = text.lower()
        currtext.insert("insert", text)
        self.key()

    def biggerview(self) -> None:
        if not self.tabs:
            return
        currtext = self.tabs[self.get_tab()].textbox
        if not currtext.tag_ranges("sel"):
            return
        selected_text = currtext.get("sel.first -1c linestart", "sel.last lineend")
        win = tk.Toplevel(self.master)
        win.resizable(0, 0)
        win.transient(self.master)
        textframe = EnhancedTextFrame(win)
        textframe.set_first_line(1)
        textframe.text.insert("insert", selected_text)
        textframe.text["state"] = "disabled"
        textframe.text.lexer = currtext.lexer
        textframe.pack(fill="both", expand=1)
        create_tags(textframe.text)
        recolorize(textframe.text)
        win.mainloop()

    def test(self):
        TestDialog(self.master, self.filetree.path)

    def check_updates(self, popup=True) -> list:
        if "DEV" in VERSION:
            ErrorInfoDialog(
                self.master,
                "Updates aren't supported by develop builds,\n\
            since you're always on the latest version!",
            )  # If you're on the developer build, you don't need updates!
            return [True, 'about://blank']
        download_file(
            url="https://raw.githubusercontent.com/ZCG-coder/NWSOFT/master/PyPlusWeb/ver.json"
        )
        with open("ver.json") as f:
            newest = json.load(f)
        version = newest["version"]
        if not popup:
            os.remove("ver.json")
            return [version != VERSION, newest["url"]]
        updatewin = tk.Toplevel(self.master)
        updatewin.title("Updates")
        updatewin.resizable(0, 0)
        updatewin.transient(self.master)
        ttkthemes.ThemedStyle(updatewin)
        if version != VERSION:
            ttk.Label(updatewin, text="Update available!", font="Arial 30").pack(
                fill="both"
            )
            ttk.Label(updatewin, text=version).pack(fill="both")
            ttk.Label(updatewin, text=newest["details"]).pack(fill="both")
            url = newest["url"]
            ttk.Button(
                updatewin, text="Get this update", command=lambda: webbrowser.open(url)
            ).pack()
        else:
            ttk.Label(updatewin, text="No updates available", font="Arial 30").pack(
                fill="both"
            )
        os.remove("ver.json")
        updatewin.mainloop()

    def git(self, action=None) -> None:
        currdir = self.filetree.path
        if action == "clone":
            dialog = InputStringDialog(self.master, "Clone", "Remote git url:")
            url = dialog.result
            if not url:
                return
            subprocess.Popen(f"git clone {url} > {os.devnull}", shell=True, cwd=currdir)
            return
        if not os.path.exists(path := os.path.join(currdir, ".git")):
            ErrorInfoDialog(self.master, f"Not a git repository: {Path(path).parent}")
            return
        if action == "init":
            subprocess.Popen(
                'git init && git add . && git commit -am "Added files"',
                shell=True,
                cwd=currdir,
            )
        elif action == "commit":
            CommitView(self.master, currdir)
        elif action == "remote":
            RemoteView(self.master, currdir)

    def indent(self, action="indent") -> None:
        """Indent/unindent feature."""
        if not self.tabs:
            return
        currtext = self.tabs[self.get_tab()].textbox
        if currtext.tag_ranges("sel"):
            sel_start = currtext.index("sel.first linestart")
            sel_end = currtext.index("sel.last lineend")
        else:
            sel_start = currtext.index("insert linestart")
            sel_end = currtext.index("insert lineend")
        if action == "indent":
            selected_text = currtext.get(sel_start, sel_end)
            indented = []
            for line in selected_text.splitlines():
                indented.append(" " * self.tabwidth + line)
            currtext.delete(sel_start, sel_end)
            currtext.insert(sel_start, "\n".join(indented))
            currtext.tag_remove("sel", "1.0", "end")
            currtext.tag_add("sel", sel_start, f"{sel_end} +4c")
            self.key()
        elif action == "unindent":
            selected_text = currtext.get(sel_start, sel_end)
            unindented = []
            for line in selected_text.splitlines():
                if line.startswith(" " * self.tabwidth):
                    unindented.append(line[4:])
                else:
                    return
            currtext.delete(sel_start, sel_end)
            currtext.insert(sel_start, "\n".join(unindented))
            currtext.tag_remove("sel", "1.0", "end")
            currtext.tag_add("sel", sel_start, sel_end)
            self.key()
        else:
            raise EditorErr("Action undefined.")

    def comment_lines(self, _=None):
        """Comments the selection or line"""
        try:
            currtext = self.tabs[self.get_tab()].textbox
            if not currtext.comment_marker:
                return
            comment_markers = currtext.comment_marker.split(" ")
            block = len(comment_markers) == 2
            if block and comment_markers[1] != "":
                comment_start = comment_markers[0]
                comment_end = comment_markers[1]
            else:
                comment_start = currtext.comment_marker
                comment_end = ""
            if currtext.tag_ranges("sel"):
                start_index, end_index = "sel.first linestart", "sel.last lineend"
                text = currtext.get(start_index, end_index)
                currtext.delete(start_index, end_index)
                if block:
                    if text.startswith(comment_start):
                        currtext.insert(
                            "insert", text[len(comment_start) : -len(comment_end)]
                        )
                        self.key()
                        return
                    currtext.insert("insert", f"{comment_start} {text} {comment_end}")
                    self.key()
                    return
                for line in currtext.get(start_index, end_index).splitlines():
                    if line.startswith(comment_start) and line.endswith(comment_end):
                        currtext.insert(
                            "insert",
                            f"{line[len(comment_start) + 1:len(comment_end) + 1]}\n",
                        )
                    else:
                        currtext.insert(
                            "insert", f"{comment_start}{line}{comment_end}\n"
                        )
            else:
                start_index, end_index = "insert linestart", "insert lineend"
                line = currtext.get(start_index, end_index)
                currtext.delete(start_index, end_index)
                if line.startswith(comment_start) and line.endswith(comment_end):
                    currtext.insert(
                        "insert", f"{line[len(comment_start):len(comment_end)]}\n"
                    )
                else:
                    currtext.insert("insert", f"{comment_start}{line}{comment_end}\n")
            self.key()
        except (KeyError, AttributeError):
            return
