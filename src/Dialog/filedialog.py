from typing import *

from src.modules import tk, ttk
from src.Utils.images import get_image
from src.Widgets.tkentry import Entry
from src.Widgets.treeview import FileTree
from src.Widgets.winframe import WinFrame


class FileOpenDialog(FileTree):
    def __init__(
        self,
        master: Union[Literal["."], tk.Misc] = ".",
        opencommand: callable = None,
        action: str = "Open",
    ):
        self._style = ttk.Style()
        self.win = WinFrame(master, action, icon=get_image("open"))
        self.buttonframe = ttk.Frame(self.win)
        self.okbtn = ttk.Button(self.buttonframe, text=action, command=self.open)
        self.okbtn.pack(side="left")
        self.cancelbtn = ttk.Button(
            self.buttonframe, text="Cancel", command=self.win.destroy
        )
        self.cancelbtn.pack(side="right")
        self.buttonframe.pack(side="bottom", anchor="nw")
        self.entryframe = ttk.Frame(self.win)
        self.pathentry = Entry(self.entryframe)
        self.pathentry.pack(side="left")
        self.set_path_btn = ttk.Button(
            self.entryframe, command=self.goto_path, text="Go", takefocus=False
        )
        self.set_path_btn.pack(side="right")
        self.entryframe.pack(fill="x")
        super().__init__(master=self.win, opencommand=opencommand)
        self.temp_path = []

    def open(self):
        item = self.tree.focus()
        item_text = self.tree.item(item, "text")
        self.get_parent(item)
        self.opencommand(f"{self.temp_path[0]}/{item_text}")
        self.master.destroy()

    def goto_path(self, _=None):
        old_path = self.path
        path = self.pathentry.get()
        try:
            self.set_path(path)
        except FileNotFoundError:
            self.path = old_path

    def on_double_click_treeview(self, event=None, **kwargs):
        super().on_double_click_treeview(event, destroy=True)


class FileSaveAsDialog(FileOpenDialog):
    def __init__(self, master, savecommand: callable):
        super().__init__(master, savecommand, "Save")
        self.win.titlebar["image"] = get_image("save-as")


class DirectoryOpenDialog(FileOpenDialog):
    def __init__(self, master, opencommand):
        self.opencommand = opencommand
        super().__init__(master, opencommand=opencommand)

    def process_directory(self, parent, showdironly: bool = False, path: str = ""):
        super().process_directory(parent, False, path)

    def open(self):
        if not self.tree.focus():
            path = self.root_node_path
            self.opencommand(path)
            self.master.destroy()
            return
        self.opencommand(self.get_path(self.tree.focus(), append_name=True))
        self.master.destroy()
