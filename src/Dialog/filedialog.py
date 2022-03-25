from src.Dialog.commondialog import get_theme
from src.Widgets.treeview import FileTree
from src.Widgets.winframe import WinFrame
from src.modules import os, ttk, ttkthemes


class FileOpenDialog(FileTree):
    def __init__(self, master=".", opencommand: callable = None, action: str = "Open"):
        self._style = ttkthemes.ThemedStyle()
        self._style.set_theme(get_theme())
        self.win = WinFrame(master, action)
        self.buttonframe = ttk.Frame(self.win)
        self.okbtn = ttk.Button(self.buttonframe, text=action, command=self.open)
        self.okbtn.pack(side="left")
        self.cancelbtn = ttk.Button(
            self.buttonframe, text="Cancel", command=self.win.destroy
        )
        self.cancelbtn.pack(side="right")
        self.buttonframe.pack(side="bottom", anchor="nw")
        self.entryframe = ttk.Frame(self.win)
        self.pathentry = ttk.Entry(self.entryframe)
        self.pathentry.pack(fill="x")
        self.open_from_string_btn = ttk.Button(
            self.pathentry, command=self.open_from_string, text=action
        )
        self.open_from_string_btn.pack(side="right")
        self.entryframe.pack(fill="x")
        super().__init__(master=self.win, opencommand=opencommand)
        self.temp_path = []

    def open(self):
        item = self.tree.focus()
        item_text = self.tree.item(item, 'text')
        self.get_parent(item)
        self.opencommand(f'{self.temp_path[0]}/{item_text}')
        self.master.destroy()

    def open_from_string(self, _=None):
        try:
            file = self.pathentry.get()
            if os.path.isfile(file):
                self.opencommand(file)
                return
            path = self.path
            file = os.path.join(path, self.pathentry.get())
            if os.path.isdir(file):
                self.path = file
                self.refresh_tree()
            else:
                self.opencommand(file)
        except FileNotFoundError:
            pass
        finally:
            self.master.destroy()

    def on_double_click_treeview(self, event=None, **kwargs):
        super().on_double_click_treeview(event, destroy=True)


class FileSaveAsDialog(FileOpenDialog):
    def __init__(self, master, savecommand: callable):
        super().__init__(master, savecommand, "Save")


class DirectoryOpenDialog(FileOpenDialog):
    def __init__(self, master, opencommand):
        self.opencommand = opencommand
        super().__init__(master, opencommand=opencommand)

    def open(self):
        self.opencommand(
            os.path.join(self.path, self.tree.item(self.tree.focus(), "text"))
        )
        self.master.destroy()
