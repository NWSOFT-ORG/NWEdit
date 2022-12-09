# coding: utf-8
"""
The editor object
The editor is a combination of widgets
TODO: Make it plugin-based
"""

import logging
import os
import sys
import threading
import tkinter as tk
import traceback
from tkinter import ttk
from typing import Callable, Union

import json5rw as json

from src.Components.autocomplete import CompleteDialog
from src.Components.commondialog import ErrorInfoDialog, YesNoDialog
from src.Components.customenotebook import ClosableNotebook
from src.Components.debugdialog import ErrorReportDialog
from src.Components.filedialog import FileOpenDialog, FileSaveAsDialog
from src.Components.hexview import HexView
from src.Components.panel import CustomTabs
from src.Components.statusbar import Statusbar
from src.Components.tktext import EnhancedText, EnhancedTextFrame, TextOpts
from src.Components.treeview import FileTree
from src.constants import APPDIR, events, logger, OSX
from src.highlighter import recolorize_line
from src.SettingsParser.extension_settings import (
    CommentMarker,
    FileTreeIconSettings,
    FormatCommand, Linter,
    PygmentsLexer, RunCommand,
)
from src.SettingsParser.menu import Menu, TouchBar
from src.SettingsParser.plugin_settings import Plugins
from src.SettingsParser.project_settings import RecentProjects
from src.Utils.functions import is_binary_string

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


class Tabs(dict):
    def __init__(self):
        super().__init__()
        self.trigger = lambda _: None

    def set_trigger(self, trigger: Callable):
        self.trigger = trigger
        self.trigger(self)

    def __setitem__(self, key, value):
        super().__setitem__(key, value)
        self.trigger(self)

    def __delitem__(self, v) -> None:
        super().__delitem__(v)
        self.trigger(self)

    def pop(self, name: str) -> None:
        super().pop(name)
        self.trigger(self)


class Editor:
    """The editor class."""

    # noinspection PyBroadException
    def __init__(self, master: tk.Toplevel, project_name: str) -> None:
        """The editor object, the entire thing that goes in the
        window."""
        self.master: tk.Toplevel = master
        self.project = project_name

        try:
            self.projects = RecentProjects(master)
            logger.debug("Project settings loaded")

            self.tabs = Tabs()  # Modified dict

            self.panedwin = ttk.Panedwindow(master, orient="horizontal")
            self.panedwin.pack(fill="both", expand=1)
            self.mainframe = ttk.Frame(self.panedwin)
            self.mainframe.pack(fill="both", expand=1)
            self.panedwin.add(self.mainframe)
            logger.debug("UI initialised")

            self.left_panel()
            self.bottom_panel()
            self.statusbar = Statusbar()
            logger.debug("Layout created")

            self.menu_obj = Menu(self, "main")
            self.tabs.set_trigger(self.menu_obj.disable)
            self.menu_obj.load_config()

            master["menu"] = self.menu_obj.menu
            logger.debug("All menus loaded.")

            if OSX:  # TouchBar support
                touchbar = TouchBar(self, True)
                touchbar.create_touchbar()
                logger.debug(f"{OSX = }, therefore enable TouchBar support")

            self.plugins_settings_class = Plugins(master, self.menu_obj)
            self.plugins_settings_class.load_plugins()
            logger.debug("Plugins loaded")

            self.create_bindings()
            self.load_status()
            self.update_title()
        except Exception:
            logger.exception("Error when initializing:")
            ErrorReportDialog(
                master, "Error when starting.", traceback.format_exc()
            )
            sys.exit(1)

    def left_panel(self):
        self.left_tabs = CustomTabs(self.panedwin)
        self.filetree = FileTree(self.left_tabs, self.open_file, self.projects.get_path_to(self.project))
        self.panedwin.insert(0, self.left_tabs)
        self.left_tabs.add(self.filetree, text="Files")

    def bottom_panel(self):
        self.bottom_panedwin = ttk.Panedwindow(self.mainframe)

        self.nb = ClosableNotebook(self.bottom_panedwin, self.close_tab)
        self.nb.enable_traversal()

        self.bottom_panedwin.pack(side="bottom", fill="both", expand=1)
        self.bottom_panedwin.add(self.nb, weight=4)
        self.bottom_tabs = CustomTabs(self.bottom_panedwin)
        self.bottom_panedwin.add(self.bottom_tabs, weight=1)

    def create_bindings(self):
        # Mouse bindings
        self.master.bind("<<MouseEvent>>", self.mouse)
        self.master.event_add("<<MouseEvent>>", "<ButtonRelease>")
        # EventClass bindings
        events.on("editor.open_file", self.open_file)
        events.on("editor.reload", self.reload)
        logger.debug("Bindings created")

    @staticmethod
    def create_text_widget(frame: ClosableNotebook) -> EnhancedText:
        """Creates a text widget in a frame."""
        textframe = EnhancedTextFrame(frame)
        # The one with line numbers, and a nice dark theme
        textframe.pack(fill="both", expand=1, side="right")
        textframe.set_first_line(1)

        textbox = textframe.text  # text widget
        textbox.frame = frame  # The text will be packed into the frame.
        textbox.focus_set()
        logger.debug("Textbox created")
        return textbox

    def update_title(self, _=None) -> str:
        try:
            path = self.tabs[self.nb.get_tab].file_dir
            if self.tabs[self.nb.get_tab].istoolwin:
                self.master.title("NWEdit")
                logger.debug("update_title: Finished early")
                return "break"
            if OSX:
                self.master.attributes("-titlepath", path)
            self.master.title(f"NWEdit [{self.project}] — {os.path.basename(path)}")
        except KeyError:
            self.master.title(f"NWEdit [{self.project}]")
            self.master.attributes("-titlepath", "")
        finally:
            return "break"

    def update_statusbar(self, _=None) -> str:
        try:
            currtext = self.get_text
            if not currtext:
                self.statusbar.label3.config(text="")
                return "break"
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

    def __key(self, event: tk.Event = None) -> None:
        """Event when a key is pressed."""
        try:
            if hasattr(event, "char") and not event.char:  # No input, no action
                return
            currtext = self.get_text
            if not currtext:
                return
            recolorize_line(currtext, currtext.lexer)
            currtext.edit_separator()
            currtext.see("insert")

            prev_completes = currtext.master.children
            for widget in prev_completes.values():
                if isinstance(widget, CompleteDialog):
                    widget.destroy()
                    break

            CompleteDialog(currtext.master, currtext, self.key).insert_completions()
            # Auto-save
            self.save_file()
            self.update_statusbar()
            # Update statusbar and title bar
            self.update_title()
            logger.debug("update_title: OK")
        except KeyError:
            self.master.bell()
            logger.exception("Error when handling keyboard event:")
        except tk.TclError:
            pass

    def key(self, event: tk.Event = None) -> None:
        """Run the key event in a separate thread"""
        thread = threading.Thread(target=self.__key, args=(event,))
        thread.daemon = True
        thread.run()

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

    def load_status(self):
        with open("EditorStatus/window_status.json") as f:
            geometry = json.load(f)
            if geometry is None or "windowGeometry" not in geometry.keys():
                return
            geometry = geometry["windowGeometry"]
            self.master.geometry(geometry)
        tree_stat = self.projects.get_treeview_stat(self.project)
        self.filetree.load_status(tree_stat)

        files = self.projects.get_open_files(self.project)
        if files:
            for file, index in files.items():
                self.open_file(file)
                text = self.get_text_editor
                if not text:
                    break
                text.mark_set("insert", index)
                text.see("insert")
        if text := self.get_text_editor:
            text.focus_set()
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
            textbox = self.create_text_widget(self.nb)
            textframe = textbox.master

            with open(file) as f:
                # Puts the contents of the file into the text widget.
                textbox.insert("end", f.read())

            textframe.icon = FileTreeIconSettings().get_icon(extens)
            textbox.controller = self.tabs[textframe] = Document(textframe, textbox, file)
            # noinspection PyTypeChecker
            self.nb.add(textframe, text=os.path.basename(file), image=textframe.icon, compound="left")
            self.nb.select(textframe)

            textbox.focus_set()
            textbox.set_lexer(PygmentsLexer().get_settings(extens))
            textbox.lint_cmd = Linter().get_settings(extens)
            textbox.cmd = RunCommand().get_settings(extens)
            textbox.format_command = FormatCommand().get_settings(extens)
            textbox.comment_marker = CommentMarker().get_settings(extens)

            textbox.see("insert")
            textbox.event_generate("<<Key>>")
            textbox.focus_set()
            textbox.edit_reset()

            TextOpts(self.master, keyaction=self.key).set_text(textbox)

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
                    file.write(self.tabs[curr_tab].textbox.get(1.0, "end"))
                    file.truncate(file.tell() - 1)
                    logger.debug("Wrote file")
            else:
                ErrorInfoDialog(self.master, "File read only")
                logger.error("Cannnot save a read-only file")
        except KeyError:
            pass

    @staticmethod
    def get_focus_widget(base_widget: tk.Misc, cls):
        if isinstance(base_widget, cls):
            return base_widget
        while hasattr(base_widget, "master"):
            base_widget = base_widget.master
            if isinstance(base_widget, cls):
                return base_widget

    def close_tab(self, event=None) -> None:
        try:
            selected_tab = None
            nb = self.mainframe.focus_get()
            nb = self.get_focus_widget(nb, ClosableNotebook)

            if isinstance(nb, ClosableNotebook):
                # noinspection DuplicatedCode
                if nb.index("end"):
                    # Close the current tab if close is selected from the file menu, or
                    # keyboard shortcut.
                    if event is None or event.type == str(2):
                        selected_tab = nb.get_tab
                    # Otherwise, close the tab based on coordinates of center-click.
                    else:
                        try:
                            index = event.widget.index(f"@{event.x},{event.y}")
                            selected_tab = nb.nametowidget(nb.tabs()[index])
                        except tk.TclError:
                            return

                nb.forget(selected_tab)
                self.tabs.pop(selected_tab)

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

    def save_status(self):
        file_list = {}

        if self.get_text_editor:
            for tab in self.tabs.values():
                if tab.istoolwin:
                    continue
                cursor_pos = tab.textbox.index("insert")
                file_list[tab.file_dir] = cursor_pos
            file_list[self.tabs[self.nb.get_tab].file_dir] = self.get_text_editor.index(
                "insert"
            )  # Open the current file
        self.projects.set_open_files(self.project, file_list)

        with open("EditorStatus/window_status.json", "w") as f:
            status = {}
            self.master.update()
            geometry = self.master.winfo_geometry()
            status["windowGeometry"] = geometry
            json.dump(status, f)

        logger.debug("Saved status")

    def exit(self) -> None:
        tree_stat = self.filetree.generate_status()
        self.projects.set_tree_status(self.project, tree_stat)

        self.save_status()

        logger.info("Close window")
        self.master.withdraw()

    def restart(self) -> None:
        self.save_status()
        os.execv(sys.executable, [__file__] + sys.argv)

    @property
    def get_text(self) -> Union[EnhancedText, None]:
        text = self.mainframe.focus_get()
        text = self.get_focus_widget(text, tk.Text)
        # noinspection PyTypeChecker
        return text

    @property
    def get_text_editor(self) -> Union[EnhancedText, None]:
        try:
            return self.tabs[self.nb.get_tab].textbox
        except KeyError:
            return

    def git(self, _=None) -> None:
        pass
