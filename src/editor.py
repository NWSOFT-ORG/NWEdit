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
import traceback

from src.Dialog.autocomplete import CompleteDialog
from src.Dialog.commondialog import (ErrorInfoDialog, InputStringDialog, YesNoDialog)
from src.Dialog.debugdialog import (ErrorReportDialog)
from src.Dialog.filedialog import DirectoryOpenDialog, FileOpenDialog, FileSaveAsDialog
from src.Dialog.goto import Navigate
from src.Git.gitview import GitView
from src.Menu.create_menu import create_menu
from src.Widgets.customenotebook import ClosableNotebook
from src.Widgets.hexview import HexView
from src.Widgets.panel import CustomTabs
from src.Widgets.statusbar import Statusbar
from src.Widgets.tktext import EnhancedText, EnhancedTextFrame, TextEditingPlugin
from src.Widgets.treeview import FileTree
from src.Widgets.winframe import WinFrame
from src.codefunctions import CodeFunctions
from src.constants import (
    APPDIR,
    MAIN_KEY,
    OSX,
    logger,
)
from src.functions import (
    is_binary_string,
    is_dark_color,
)
from src.functions import lighten_color
from src.highlighter import recolorize_line
from src.modules import (
    Path,
    logging,
    os,
    subprocess,
    tk,
    ttk,
    ttkthemes,
    font,
)
from src.settings import (
    CommentMarker,
    FormatCommand,
    PygmentsLexer,
    Linter,
    RunCommand,
    Settings,
)
from src.Menu.menubar import MenuBar

if OSX:
    # noinspection PyUnresolvedReferences
    from src.modules import PyTouchBar

os.chdir(APPDIR)  # Need to change to the correct directory


class Document:
    """Helper class, for the editor. It holds all the data which a tab has"""

    def __init__(self,
                 frame=None,
                 textbox=None,
                 file_dir: str = '',
                 istoolwin: bool = False) -> None:
        self.frame = frame
        self.file_dir = file_dir
        self.textbox = textbox
        self.istoolwin = istoolwin


class Editor:
    """The editor class."""

    def __init__(self, master: tk.Tk) -> None:
        """The editor object, the entire thing that goes in the
        window."""
        # noinspection PyBroadException
        try:
            self.settings_class = Settings()
            self.file_settings_class = PygmentsLexer()
            self.linter_settings_class = Linter()
            self.cmd_settings_class = RunCommand()
            self.format_settings_class = FormatCommand()
            self.commet_settings_class = CommentMarker()
            self.master = master
            self.opts = TextEditingPlugin(keyaction=self.key)

            self.theme = self.settings_class.get_settings("theme")
            self.tabwidth = self.settings_class.get_settings("tab")
            logger.debug("Settings loaded")

            self.master.geometry("1200x800")
            self.style = ttkthemes.ThemedStyle(self.master)
            self.style.set_theme(self.theme)
            self.bg = self.style.lookup("TLabel", "background")
            self.fg = self.style.lookup("TLabel", "foreground")
            if is_dark_color(self.bg):
                self.close_icon = tk.PhotoImage(file="Images/close.gif")
                self.open_icon = tk.PhotoImage(file="Images/open.gif")
                self.clone_icon = tk.PhotoImage(file="Images/clone.gif")
            else:
                self.close_icon = tk.PhotoImage(file="Images/close-dark.gif")
                self.open_icon = tk.PhotoImage(file="Images/open-dark.gif")
                self.clone_icon = tk.PhotoImage(file="Images/clone-dark.gif")

            self.new_icon = tk.PhotoImage(file="Images/new.gif")
            self.reload_icon = tk.PhotoImage(file="Images/reload.gif")
            self.save_as_icon = tk.PhotoImage(file="Images/saveas.gif")
            logger.debug("Icons loaded")
            self.icon = tk.PhotoImage(file="Images/pyplus.gif")
            self.master.iconphoto(True, self.icon)
            logger.debug("Theme loaded")

            self.tabs = {}

            self.menubar = MenuBar(self.master)
            self.panedwin = ttk.Panedwindow(self.master, orient="horizontal")
            self.panedwin.pack(fill="both", expand=True)
            self.mainframe = ttk.Frame(self.master)
            self.mainframe.pack(fill='both', expand=True)
            self.panedwin.add(self.mainframe)

            self.left_panel()
            self.bottom_panel()
            self.statusbar = Statusbar()

            self.codefuncs = CodeFunctions(self.master, self.tabs, self.nb, self.bottom_tabs)

            if OSX:
                PyTouchBar.prepare_tk_windows(self.master)
                open_button = PyTouchBar.TouchBarItems.Button(
                    image="Images/open.gif", action=lambda: self.open_file()
                )
                save_as_button = PyTouchBar.TouchBarItems.Button(
                    image="Images/saveas.gif", action=lambda: self.save_as()
                )
                close_button = PyTouchBar.TouchBarItems.Button(
                    image="Images/close.gif", action=self.close_tab
                )
                space = PyTouchBar.TouchBarItems.Space.Flexible()
                run_button = PyTouchBar.TouchBarItems.Button(
                    image="Images/run.gif", action=self.codefuncs.run
                )
                PyTouchBar.set_touchbar(
                    [open_button, save_as_button, close_button, space, run_button]
                )
            create_menu(self)
            editmenus = self.opts.create_menu(self.master)
            self.right_click_menu = editmenus[1]
            self.create_bindings()
            self.reopen_files()
            self.update_title()
        except Exception:
            logger.exception("Error when initializing:")
            ErrorReportDialog('Error when starting.', traceback.format_exc())

    def left_panel(self) -> None:
        self.left_tabs = CustomTabs(self.panedwin)
        self.filetree = FileTree(self.left_tabs, self.open_file)
        self.panedwin.insert(0, self.left_tabs)
        self.left_tabs.add(self.filetree, text='Files')

    def bottom_panel(self) -> None:
        self.bottom_panedwin = ttk.Panedwindow(self.mainframe)

        self.nb = ClosableNotebook(self.bottom_panedwin, self.close_tab)
        self.nb.event_add('<<Click>>', '<1>')
        self.nb.bind("<<Click>>", self.click_tab)

        self.nb.enable_traversal()

        self.bottom_panedwin.pack(side='bottom', fill='both', expand=True)
        self.bottom_panedwin.add(self.nb, weight=3)
        self.bottom_tabs = CustomTabs(self.bottom_panedwin)
        self.bottom_panedwin.add(self.bottom_tabs, weight=1)

    def click_tab(self, _: tk.Event = None):
        try:
            self.opts.set_text(self.get_text())
        except AttributeError:
            pass

    def create_bindings(self) -> None:
        # Keyboard bindings
        self.master.bind(f"<{MAIN_KEY}-w>", self.close_tab)
        self.master.bind(f"<{MAIN_KEY}-o>", lambda _: self.open_file())
        # Mouse bindings
        self.master.bind("<<MouseEvent>>", self.mouse)
        self.master.event_add("<<MouseEvent>>", "<ButtonRelease>")

        self.master.protocol(
            "WM_DELETE_WINDOW", lambda: self.quit_editor(force=True)
        )  # When the window is closed, or quit from Mac, do exit action
        self.master.createcommand("::tk::mac::Quit", self.quit_editor)
        logger.debug("Bindings created")

    def start_screen(self) -> None:
        frame = WinFrame(self.master, 'Start', self.bg)

        canvas_bg = lighten_color(self.bg, 10, 10, 10)
        first_tab = tk.Canvas(frame, background=canvas_bg, highlightthickness=0)
        first_tab.icon = tk.PhotoImage(file='Images/pyplus-35px.gif')
        frame.add_widget(first_tab)

        first_tab.create_image(20, 20, anchor="nw", image=first_tab.icon)
        fg = "#8dd9f7" if is_dark_color(self.bg) else "blue"
        bold = font.Font(family="Arial", size=35, weight="bold")
        first_tab.create_text(
            60,
            10,
            anchor="nw",
            text="Welcome!",
            font=bold,
            fill=self.fg,
            tags="link",
        )
        label1 = ttk.Label(
            first_tab,
            text="Open file",
            foreground=fg,
            background=canvas_bg,
            cursor="hand2",
            compound="left",
            image=self.open_icon,
        )
        label2 = ttk.Label(
            first_tab,
            text="New...",
            foreground=fg,
            background=canvas_bg,
            cursor="hand2",
            compound="left",
            image=self.new_icon,
        )
        label3 = ttk.Label(
            first_tab,
            text="Clone",
            foreground=fg,
            background=canvas_bg,
            compound="left",
            image=self.clone_icon,
            cursor="hand2",
        )
        label4 = ttk.Label(
            first_tab,
            text="Close",
            foreground=fg,
            background=canvas_bg,
            cursor="hand2",
            compound="left",
            image=self.close_icon,
        )

        links = [label1, label2, label3, label4]

        label1.bind("<Button>", lambda _: self.open_file())
        label2.bind("<Button>", self.filetree.new_file)
        label4.bind("<Button>", lambda _: frame.destroy())
        label3.bind("<Button>", lambda _: self.git("clone"))

        for y_index, item in enumerate(links):
            first_tab.create_window(50, 100 + (y_index - 1) * 40, window=item, anchor="nw")
            item.bind('<Button>', lambda _: frame.destroy(), add=True)

        logger.debug("Start screen created")

    def create_text_widget(self, frame: ttk.Frame) -> EnhancedText:
        """Creates a text widget in a frame."""

        panedwin = ttk.Panedwindow(frame)
        panedwin.pack(fill="both", expand=True)

        textframe = EnhancedTextFrame(panedwin)
        # The one with line numbers and a nice dark theme
        textframe.pack(fill="both", expand=True, side="right")
        panedwin.add(textframe)
        textframe.panedwin = panedwin
        textframe.set_first_line(1)

        textbox = textframe.text  # text widget
        textbox.panedwin = panedwin
        textbox.complete = CompleteDialog(textframe, textbox)
        textbox.frame = frame  # The text will be packed into the frame.
        textbox.bind(("<Button-2>" if OSX else "<Button-3>"), self.right_click)
        textbox.bind(f"<{MAIN_KEY}-b>", self.codefuncs.run)
        textbox.bind(f"<{MAIN_KEY}-f>", self.codefuncs.search)
        textbox.bind(f"<{MAIN_KEY}-n>", self.filetree.new_file)
        textbox.bind(f"<{MAIN_KEY}-N>", lambda _=None: Navigate(self.get_text()))
        textbox.bind(f"<{MAIN_KEY}-r>", self.reload)
        textbox.bind(f"<{MAIN_KEY}-S>", lambda _=None: self.save_as())
        textbox.focus_set()
        logger.debug("Textbox created")
        return textbox

    def update_title(self, _: tk.Event = None) -> str:
        try:
            if self.tabs[self.nb.get_tab()].istoolwin:
                self.master.title("PyPlus")
                logger.debug("update_title: Finished early")
                return "break"
            self.master.title(f"PyPlus -- {self.tabs[self.nb.get_tab()].file_dir}")
        except KeyError:
            self.master.title("PyPlus")
        finally:
            return "break"

    def update_statusbar(self, _: tk.Event = None) -> str:
        try:
            if not self.tabs:
                self.statusbar.label3.config(text="")
                return "break"
            currtext = self.get_text()
            index = currtext.index("insert")
            ln = index.split(".")[0]
            col = index.split(".")[1]
            self.statusbar.label3.config(text=f"Line {ln} Col {col}")
            logger.debug("update_statusbar: OK")
        except KeyError:
            self.statusbar.label3.config(text='')
            logger.exception("Error:")
        finally:
            return "break"

    def key(self, _: tk.Event = None) -> None:
        """Event when a key is pressed."""
        try:
            currtext = self.get_text()
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

    def mouse(self, _: tk.Event = None) -> None:
        """The action done when the mouse is clicked"""
        try:
            self.update_statusbar()
            # Update statusbar and title bar
            self.update_title()
            logger.debug("update_title: OK")
        except KeyError:
            self.master.bell()
            logger.exception("Error when handling mouse event:")

    def reopen_files(self) -> None:
        with open("Backups/recent_files.txt") as f:
            if not f.read().strip():
                self.start_screen()
                return
            for line in f.read().split("\n"):
                if line:
                    self.open_file(line, askhex=False)
        with open("Backups/recent_dir.txt") as f:
            self.filetree.path = f.read()
            self.filetree.refresh_tree()
        self.update_title()
        self.update_statusbar()

    def open_hex(self, file="") -> None:
        if not file:
            FileOpenDialog(self.open_hex)
        file = os.path.abspath(file)
        logger.info("HexView: opened")
        viewer = ttk.Frame(self.master)
        viewer.focus_set()
        window = HexView(viewer)
        window.open(file)
        self.tabs[viewer] = Document(viewer, EnhancedText, file)
        self.nb.add(viewer, text=f"Hex -- {os.path.basename(file)}")
        self.nb.select(viewer)
        self.update_title()
        self.update_statusbar()
        return window.textbox

    def open_dir(self, directory: str = "") -> None:
        if not directory:
            DirectoryOpenDialog(self.open_dir)
            return

        self.filetree.path = directory
        self.filetree.refresh_tree()

    def open_file(self, file: str = "", askhex: bool = True) -> [EnhancedText, None]:
        """Opens a file
        If a file is not provided, a messagebox'll
        pop up to ask the user to select the path."""
        if not file:
            FileOpenDialog(self.open_file)

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
                    return self.get_text()
                self.open_hex(file)
                return self.get_text()

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
            textbox.format_command = self.format_settings_class.get_settings(
                extens
            )
            textbox.comment_marker = self.commet_settings_class.get_settings(
                extens
            )

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
            if name == 'IsADirectoryError':
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
                FileSaveAsDialog(self.save_as)
                return
            curr_tab = self.nb.get_tab()
            if not file_dir:
                return

            self.tabs[curr_tab].file_dir = file_dir
            self.nb.tab(curr_tab, text=os.path.basename(file_dir))
            with open(file_dir, "w") as f:
                f.write(self.tabs[curr_tab].textbox.get(1.0, "end"))
            self.update_title()
            self.reload()

    def save_file(self, _: tk.Event = None) -> None:
        """Save an *existing* file"""
        try:
            curr_tab = self.nb.get_tab()
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

    def right_click(self, event: tk.Event) -> None:
        if self.tabs:
            self.right_click_menu.tk_popup(event.x_root, event.y_root)

    def close_tab(self, event: tk.Event = None, show_startscreen: bool = True) -> None:
        try:
            selected_tab = None
            if self.nb.index("end"):
                # Close the current tab if close is selected from file menu, or
                # keyboard shortcut.
                if event is None or event.type == str(2):
                    selected_tab = self.nb.get_tab()
                # Otherwise, close the tab based on coordinates of center-click.
                else:
                    try:
                        index = event.widget.index("@%d,%d" % (event.x, event.y))
                        selected_tab = self.nb.nametowidget(self.nb.tabs()[index])
                    except tk.TclError:
                        return

            self.nb.forget(selected_tab)
            self.tabs.pop(selected_tab)

            if len(self.tabs) == 0 and show_startscreen:
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
            self.close_tab(show_startscreen=False)
        for x in files:
            self.open_file(x)
        self.nb.select(curr)

    def quit_editor(self, force: bool = False) -> None:
        with open("Backups/recent_dir.txt", "w") as f:
            f.write(self.filetree.path)
        with open("Backups/recent_files.txt", "w") as f:
            file_list = ""
            for tab in self.tabs.values():
                file_list += tab.file_dir + "\n"
            f.write(file_list)
        if not force:
            self.master.destroy()
            logger.info("Window is destroyed")
        else:
            self.master.destroy()

    def restart(self) -> None:
        self.quit_editor(force=False)
        newtk = tk.Tk()
        self.__init__(newtk)
        newtk.mainloop()

    def get_text(self) -> EnhancedText:
        try:
            return self.tabs[self.nb.get_tab()].textbox
        except KeyError:
            pass

    def git(self, action: str = '') -> None:
        currdir = self.filetree.path
        if action == "clone":
            dialog = InputStringDialog(self.master, "Clone", "Remote git url:")
            url = dialog.result
            if not url:
                return
            subprocess.Popen(f"git clone {url}", shell=True, cwd=currdir)
            return
        if not os.path.exists(path := os.path.join(currdir, ".git")):
            ErrorInfoDialog(self.master, f"Not a git repository: {Path(path).parent}")
            return
        elif action == "commit":
            GitView(self.panedwin, currdir)