import os
import shutil
import tkinter as tk
from pathlib import Path
from tkinter import font, ttk
from typing import Literal

import send2trash

from src.Components.commondialog import StringInputDialog
from src.Components.fileinfodialog import FileInfoDialog
from src.Components.newitem import NewItemDialog
from src.Components.scrollbar import Scrollbar
from src.constants import logger, OSX
from src.SettingsParser.extension_settings import FileTreeIconSettings
from src.SettingsParser.interval_settings import IntervalSettings


class FileTree(ttk.Frame):
    """
    Treeview to select files
    """

    def __init__(self, path: Path, master, opencommand=None):
        self.expanded = []
        self.temp_path = []
        self._style = ttk.Style()
        self.bg = self._style.lookup("TLabel", "background")
        super().__init__(master)
        self.tree = ttk.Treeview(self, show="tree")
        self.yscroll = Scrollbar(self, command=self.tree.yview)
        self.xscroll = Scrollbar(self, command=self.tree.xview, orient="horizontal")
        self.yscroll.pack(side="right", fill="y")
        self.xscroll.pack(side="bottom", fill="x")
        self.tree["yscrollcommand"] = self.yscroll.set
        self.tree["xscrollcommand"] = self.xscroll.set
        self.master = master
        self.opencommand = opencommand
        self.root_node = None

        self.icon_settings = FileTreeIconSettings()
        self.icons = []
        self.temp_path = []  # IMPORTANT! Reset after use

        self.interval_settings = IntervalSettings()
        self.refresh_interval = self.interval_settings.get_settings("TreeviewRefresh")

        self.pack(side="left", fill="both", expand=1)
        self.tree.bind("<Double-1>", self.on_double_click_treeview)
        self.tree.tag_bind(
            "file",
            "<Button-2>" if OSX else "<Button-3>",
            lambda event: self.right_click(event),
        )
        self.tree.tag_bind(
            "subfolder",
            "<Button-2>" if OSX else "<Button-3>",
            lambda event: self.right_click(event),
        )
        self.tree.update()

        self.tree.tag_configure("subfolder", foreground="#448dc4")
        italic = font.Font(self)
        italic.config(slant="italic")
        self.tree.tag_configure("empty", font=italic, foreground="#C2FF74")

        self.tree.pack(fill="both", expand=1, anchor="nw")
        self.tree.bind("<<TreeviewOpen>>", lambda _: self.open_dir())
        self.tree.bind("<<TreeviewClose>>", lambda _: self.close_dir())
        self.set_path(path)
        child_id = self.tree.get_children()[-1]
        self.tree.selection_set(child_id)

    def remove(self, item: str) -> None:
        path = self.get_path(item, True)
        try:
            send2trash.send2trash(path)  # Send to trash is a good idea if possible
        except (send2trash.TrashPermissionError, OSError):
            # Linux OSs might have problems with the trash bin
            if path.is_dir():
                path.rmdir()
            else:
                path.unlink()
        self.refresh_tree(True)  # Reset to root path to avoid any problems

    def rename(self, item: str) -> None:
        path = self.get_path(item, True)
        dialog = StringInputDialog(self.master, "Rename", "New name:")
        if not dialog.result:
            return
        try:
            newdir = self.path / dialog.result
            shutil.move(path, newdir)
        except (IsADirectoryError, FileExistsError):
            pass
        finally:
            self.refresh_tree(True)

    def get_info(self, item: str) -> None:
        path = self.get_path(item, True)
        FileInfoDialog(self.master, path)

    def close_dir(self):
        item = self.tree.focus()
        self.expanded.remove(item)

    def open_dir(self, directory_item="") -> None:
        """Save time by loading directory only when needed, so we don't have to recursivly process the directories."""
        tree = self.tree
        if directory_item:
            item = directory_item
        else:
            item = tree.focus()
        self.expanded.append(item)

        item_text = tree.item(item, "text")

        self.temp_path = []
        self.get_parent(item)

        path = Path(*list(reversed(self.temp_path))[1:], item_text)
        if path.is_file():
            return  # Don't open files, only open directories
        logger.debug(f"Opened tree item, path: {self.path}")
        tree.delete(*tree.get_children(item))
        self.process_directory(path=self.path, parent=item)

    def process_directory(self, path: Path, parent: str, showdironly: bool = False) -> None:
        if path.is_file():
            return
        try:
            items = sorted(os.listdir(path))
        except FileNotFoundError:
            logger.exception("Path not found")
            items = []
        if not items:
            self.tree.insert(parent, "end", text="Empty", tags=("empty",))
        last_dir_index = 0
        for p in items:
            p = Path(p)
            abspath = path / p
            isdir = abspath.is_dir()
            if isdir:
                oid = self.tree.insert(
                    parent,
                    last_dir_index,
                    text=p.name,
                    tags=("subfolder",),
                    open=False,
                    image=self.icon_settings.folder_icon,
                )
                last_dir_index += 1
                if not showdironly:
                    self.tree.insert(
                        oid, 0, text="Loading...", tags=("empty",)
                    )  # Just a placeholder, will load if needed
            else:
                if showdironly:
                    return
                extension = p.suffix
                self.icons.append(self.icon_settings.get_icon(extension))
                self.tree.insert(
                    parent,
                    "end",
                    text=p.name,
                    open=False,
                    image=self.icons[-1],
                    tags=("file",),
                )

    def on_double_click_treeview(self, event: tk.Event, destroy: bool = False) -> None:
        tree = self.tree
        item = tree.identify("item", event.x, event.y)
        name = self.get_path(item, True)
        if name.is_dir():
            return
        if self.opencommand:
            self.opencommand(name)
        if destroy:
            self.master.destroy()

    def get_parent(self, item: str) -> None:
        """Find the path to item in treeview"""
        tree = self.tree
        parent_iid = tree.parent(item)
        parent_text = tree.item(parent_iid, "text")
        self.temp_path.append(parent_text)
        if parent_text:
            self.get_parent(parent_iid)

    def get_path(self, item: str, append_name: bool = False, expect_type: Literal["file", "dir"] = "file") -> Path:
        self.temp_path = []
        self.get_parent(item)
        self.temp_path.reverse()
        self.temp_path.remove("")
        if append_name:
            self.temp_path.append(self.tree.item(item, "text"))
        abspath = Path(*self.temp_path).resolve()
        if abspath.is_file() and expect_type == "dir":
            # If we're getting a file, but we're trying to get the directory, return its parent
            abspath = Path(abspath).parent
        return abspath

    def right_click(self, event: tk.Event, item: str = "") -> None:
        menu = tk.Menu(self.master)
        if not item:
            item = self.tree.identify("item", event.x, event.y)
        self.tree.selection_set(item)

        menu.add_command(label="New...", command=self.new_item)
        menu.add_separator()
        menu.add_command(label="Get Info", command=lambda: self.get_info(item))
        menu.add_separator()
        menu.add_command(label="Rename file", command=lambda: self.rename(item))
        menu.add_command(label="Move to Trash", command=lambda: self.remove(item))
        menu.add_separator()
        menu.add_command(label="Refresh", command=lambda: self.refresh_tree(False))

        menu.tk_popup(event.x_root, event.y_root)

    def refresh_tree(self, reset=False) -> None:
        self.tree.delete(*self.tree.get_children())
        if reset:
            abspath = self.orig_path.parent
        else:
            abspath = self.path.parent
        self.root_node = self.tree.insert(
            "", "end", text=abspath.as_posix(), open=True, tags=("root",)
        )
        self.process_directory(path=abspath, parent=self.root_node)

    def set_path(self, new_path: Path):
        self.tree.delete(*self.tree.get_children())
        abspath = new_path.resolve()

        self.path = abspath
        self.orig_path = abspath

        self.root_node = self.tree.insert(
            "", "end", text=abspath.as_posix(), open=True, tags=("root",)
        )
        self.process_directory(path=abspath, parent=self.root_node)

    def generate_status(self):
        status = {
            "expandedNodes"     : self.expanded,
            "yScrollbarLocation": self.yscroll.get(),
            "xScrollbarLocation": self.xscroll.get(),
        }

        return status

    def load_status(self, status):
        self.refresh_tree(True)

        for item in status["expandedNodes"]:
            try:
                self.tree.item(item, open=True)
                self.open_dir(item)
            except tk.TclError:
                pass

        self.expanded = status["expandedNodes"]

        y_scroll_location = status["yScrollbarLocation"]
        x_scroll_location = status["xScrollbarLocation"]
        self.tree.yview_moveto(y_scroll_location[0])
        self.tree.xview_moveto(x_scroll_location[0])

    def new_item(self):
        NewItemDialog(self, self.master, self.opencommand)
