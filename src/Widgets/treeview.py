from src.constants import logger, OSX
from src.Dialog.commondialog import get_theme, StringInputDialog
from src.Dialog.fileinfodialog import FileInfoDialog
from src.modules import font, json, os, send2trash, shutil, tk, ttk, ttkthemes
from src.Utils.color_utils import is_dark_color


class IconSettings:
    def __init__(self) -> None:
        self.path = "Config/file-icons.json"
        self.dark = False

    def set_theme(self, dark: bool) -> None:
        self.dark = dark

    def get_icon(self, extension: str) -> tk.PhotoImage:
        with open(self.path) as f:
            settings = json.load(f)
        try:
            icon_name = settings[extension]
        except KeyError:
            icon_name = "other"
        if self.dark:
            return tk.PhotoImage(file=f"Images/file-icons/{icon_name}-light.gif")
        else:
            return tk.PhotoImage(file=f"Images/file-icons/{icon_name}.gif")


class FileTree(ttk.Frame):
    """
    Treeview to select files
    """

    def __init__(self, master=None, opencommand=None):
        self.temp_path = []
        self._style = ttkthemes.ThemedStyle()
        self._style.set_theme(get_theme())
        self.bg = self._style.lookup("TLabel", "background")
        super().__init__(master)
        self.tree = ttk.Treeview(self, show="tree")
        self.yscroll = ttk.Scrollbar(self, command=self.tree.yview)
        self.xscroll = ttk.Scrollbar(self, command=self.tree.xview, orient="horizontal")
        self.yscroll.pack(side="right", fill="y")
        self.xscroll.pack(side="bottom", fill="x")
        self.tree["yscrollcommand"] = self.yscroll.set
        self.tree["xscrollcommand"] = self.xscroll.set
        self.master = master
        self.path = "empty/"
        self.opencommand = opencommand
        self.root_node = None

        self.icon_settings = IconSettings()
        self.icon_settings.set_theme(is_dark_color(self.bg))
        if is_dark_color(self.bg):
            self.other_icon = tk.PhotoImage(file="Images/file-icons/other-light.gif")
            self.folder_icon = tk.PhotoImage(file="Images/file-icons/folder-light.gif")
        else:
            self.other_icon = tk.PhotoImage(file="Images/file-icons/other.gif")
            self.folder_icon = tk.PhotoImage(file="Images/file-icons/folder.gif")
        self.icons = []
        self.temp_path = []  # IMPORTANT! Reset after use

        self.pack(side="left", fill="both", expand=1)
        self.refresh_tree()
        self.tree.bind("<Double-1>", self.on_double_click_treeview)
        self.tree.tag_bind(
            "file",
            "<Button-2>" if OSX else "<Button-3>",
            lambda event: self.right_click(event, False),
        )
        self.tree.tag_bind(
            "subfolder",
            "<Button-2>" if OSX else "<Button-3>",
            lambda event: self.right_click(event, True),
        )
        self.tree.update()

        self.tree.tag_configure("subfolder", foreground="#448dc4")
        italic = font.Font(self)
        italic.config(slant="italic")
        self.tree.tag_configure("empty", font=italic, foreground="#C2FF74")

        self.tree.pack(fill="both", expand=1, anchor="nw")
        self.tree.bind("<<TreeviewOpen>>", self.open_dir)

    def remove(self, item: str) -> None:
        path = self.get_path(item, True)
        try:
            send2trash.send2trash(path)  # Send to trash is a good idea if possible
        except (send2trash.TrashPermissionError, OSError):
            # Linux OSs might have problems with the trash bin
            if os.path.isdir(path):
                shutil.rmtree(path)
            else:
                os.remove(path)
        self.refresh_tree()

    def rename(self, item: str) -> None:
        path = self.get_path(item, True)
        dialog = StringInputDialog(self.master, "Rename", "New name:")
        if not dialog.result:
            return
        try:
            newdir = os.path.join(self.path, dialog.result)
            shutil.move(path, newdir)
        except (IsADirectoryError, FileExistsError):
            pass
        finally:
            self.refresh_tree()

    def get_info(self, item: str) -> None:
        path = self.get_path(item, True)
        FileInfoDialog(self.master, path)

    def new_folder(self, item: str, isdir: bool) -> None:
        win = StringInputDialog(self.master, "New Folder", "Name:")
        if name := win.result:
            item_path = self.get_path(item, isdir)
            path = os.path.join(item_path, name)
            os.mkdir(path)
        self.refresh_tree()

    def new_file(self, item: str, isdir: bool) -> None:
        win = StringInputDialog(self.master, "New File", "Name:")
        if name := win.result:
            item_path = self.get_path(item, isdir)
            path = os.path.join(item_path, name)
            with open(path, "w") as f:
                f.write("")
        self.refresh_tree()

    def open_dir(self, _) -> None:
        """Save time by loading directory only when needed, so we don't have to recursivly process the directories."""
        tree = self.tree
        item = tree.focus()
        item_text = tree.item(item, "text")
        self.temp_path = []
        self.get_parent(item)
        path = f'{"/".join(reversed(self.temp_path))[1:]}/{item_text}'
        if os.path.isfile(path):
            return
        self.path = path
        logger.debug(f"Opened tree item, path: {self.path}")
        tree.delete(*tree.get_children(item))
        self.process_directory(item, path=self.path)

    def process_directory(
            self, parent: str, showdironly: bool = False, path: str = ""
    ) -> None:
        if os.path.isfile(path):
            return
        items = sorted(os.listdir(path))
        if not items:
            self.tree.insert(parent, "end", text="Empty", tags=("empty",))
        last_dir_index = 0
        self.icons = []
        for p in items:
            abspath = os.path.join(path, p)
            isdir = os.path.isdir(abspath)
            if isdir:
                oid = self.tree.insert(
                    parent,
                    last_dir_index,
                    text=p,
                    tags=("subfolder",),
                    open=False,
                    image=self.folder_icon,
                )
                last_dir_index += 1
                if not showdironly:
                    self.tree.insert(
                        oid, 0, text="Loading..."
                    )  # Just a placeholder, will load if needed
            else:
                extension = p.split(".")
                self.icons.append(self.icon_settings.get_icon(extension[-1]))
                self.tree.insert(
                    parent,
                    "end",
                    text=p,
                    open=False,
                    image=self.icons[-1],
                    tags=("file",),
                )

    def on_double_click_treeview(self, event: tk.Event, destroy: bool = False) -> None:
        tree = self.tree
        item = tree.identify("item", event.x, event.y)
        name = self.get_path(item, True)
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

    def get_path(self, item: str, append_name: bool = False) -> str:
        self.temp_path = []
        self.get_parent(item)
        self.temp_path.reverse()
        self.temp_path.remove("")
        if append_name:
            self.temp_path.append(self.tree.item(item, "text"))
        return os.path.abspath("/".join(self.temp_path))

    def right_click(self, event: tk.Event, isdir: bool) -> None:
        menu = tk.Menu(self.master)
        item = self.tree.identify("item", event.x, event.y)
        self.tree.selection_set(item)

        new_cascade = tk.Menu(menu)
        new_cascade.add_command(
            label="New File", command=lambda: self.new_file(item, isdir)
        )
        new_cascade.add_command(
            label="New Directory", command=lambda: self.new_folder(item, isdir)
        )
        menu.add_cascade(menu=new_cascade, label="New...")
        menu.add_separator()
        menu.add_command(label="Get Info", command=lambda: self.get_info(item))
        menu.add_separator()
        menu.add_command(label="Rename file", command=lambda: self.rename(item))
        menu.add_command(label="Move to Trash", command=lambda: self.remove(item))
        menu.add_separator()
        menu.add_command(label="Refresh", command=self.refresh_tree)

        menu.tk_popup(event.x_root, event.y_root)

    def refresh_tree(self) -> None:
        path = self.path
        self.tree.delete(*self.tree.get_children())
        ypos = self.yscroll.get()
        abspath = os.path.abspath(path)
        self.root_node = self.tree.insert(
            "", "end", text=abspath, open=True, tags=("root",)
        )
        self.process_directory(self.root_node, path=abspath)
        self.yscroll.set(*ypos)
