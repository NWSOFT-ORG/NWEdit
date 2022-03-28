from src.Dialog.commondialog import InputStringDialog, YesNoDialog, get_theme
from src.Widgets.winframe import WinFrame
from src.constants import OSX, WINDOWS, logger
from src.Utils.color_utils import is_dark_color
from src.modules import os, shutil, time, tk, ttk, ttkthemes, json, font, send2trash


class IconSettings:
    def __init__(self):
        self.path = "Config/file-icons.json"
        self.dark = False

    def set_theme(self, dark: bool):
        self.dark = dark

    def get_icon(self, extension: str):
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
        self.tree.bind("<Button-2>" if OSX else "<Button-3>", self.right_click)
        self.tree.update()

        self.tree.tag_configure("subfolder", foreground="#448dc4")
        italic = font.Font(self)
        italic.config(slant="italic")
        self.tree.tag_configure("empty", font=italic, foreground="#C2FF74")

        self.tree.pack(fill="both", expand=1, anchor="nw")
        self.tree.bind("<<TreeviewOpen>>", self.open_dir)

    def remove(self, item):
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

    def rename(self, event):
        try:
            path = self.get_path(event, True)
            dialog = InputStringDialog(self.master, "Rename", "New name:")
            newdir = os.path.join(self.path, dialog.result)
            shutil.move(path, newdir)
            self.refresh_tree()
        except (IsADirectoryError, FileExistsError):
            pass

    def get_info(self, item, is_path=False):
        if not is_path:
            path = self.get_path(item, True)
        else:
            path = self.tree.item(item, "text")
        basename = os.path.basename(path)
        size = str(os.path.getsize(path))
        # Determine the correct unit
        if int(size) / 1024 < 1:
            size += " Bytes"
        elif int(size) / 1024 >= 1 <= 2:
            size = f"{int(size) // 1024} Kilobytes"
        elif int(size) / 1024 ** 2 >= 1 <= 2:
            size = f"{int(size) // 1024 ** 2} Megabytes"
        elif int(size) / 1024 ** 3 >= 1 <= 2:
            size = f"{int(size) // 1024 ** 3} Gigabytes"
        elif int(size) / 1024 ** 4 >= 1 <= 2:
            size = f"{int(size) // 1024 ** 4} Terabytes"
        # It can go on and on, but the newest PCs won't have more than a PB storage
        #      /-------------/|
        #     /                / /
        #    /  SSD           / /
        #   /   10 TB        / /
        #  /             / /
        # /             / /
        # \=============\/
        mdate = f"Last modified: {time.ctime(os.path.getmtime(path))}"
        cdate = f"Created: {time.ctime(os.path.getctime(path))}"
        win = WinFrame(self.master, "Info", False)
        ttk.Label(win, text=f"Name: {basename}").pack(side="top", anchor="nw", fill="x")
        ttk.Label(win, text=f"Path: {path}").pack(side="top", anchor="nw", fill="x")
        ttk.Label(win, text=f"Size: {size}").pack(side="top", anchor="nw", fill="x")
        ttk.Label(win, text=mdate).pack(side="top", anchor="nw", fill="x")
        ttk.Label(win, text=cdate).pack(side="top", anchor="nw", fill="x")
        if not (WINDOWS or OSX):
            ttk.Label(
                win,
                text="Note: On Linux, the dates would not be the exact date of creation or modification!",
            ).pack(side="top", anchor="nw", fill="x")
        win.mainloop()

    def new_folder(self, event=None):
        win = tk.Toplevel(master=self.master)
        win.resizable(False, False)
        win.config(background=self.bg)
        ttk.Label(win, text="Name:").pack(side="top", anchor="nw")
        filename = tk.Entry(win)
        filename.pack(side="top", anchor="nw")
        item = self.tree.item(self.tree.identify("item", event.x, event.y), "text")

        def create():
            if not filename.get():
                return
            path = f"{item}/{filename.get()}"
            try:
                os.mkdir(path)
            except FileExistsError:
                if YesNoDialog(
                        title="This directory already exsists!",
                        text="Do you want to overwrite?",
                ).result:
                    shutil.rmtree(path, ignore_errors=True)
                    os.mkdir(path)
            self.refresh_tree()

        okbtn = ttk.Button(win, text="OK", command=create)
        okbtn.pack(side="left", anchor="w", fill="x")
        cancelbtn = ttk.Button(win, text="Cancel", command=lambda: win.destroy())
        cancelbtn.pack(side="left", anchor="w", fill="x")
        win.mainloop()
        self.refresh_tree()

    def new_file(self, event=None):
        win = WinFrame(self.master, "New File", False, False)
        ttk.Label(win, text="Name:").pack(side="top", anchor="nw")
        filename = tk.Entry(win)
        filename.pack(side="top", anchor="nw")
        try:
            item = self.tree.item(
                self.tree.parent(self.tree.identify("item", event.x, event.y)), "text"
            )
        except AttributeError:
            item = self.tree.item(self.tree.parent(self.tree.focus()), "text")

        def create():
            if not filename.get():
                return
            path = f"{item}/{filename.get()}"
            if os.path.exists(path):
                YesNoDialog(
                    title="This file already exsists!",
                    text="Do you want to overwrite?",
                )
            with open(path, "w") as f:
                f.write("")
            self.opencommand(path)
            self.refresh_tree()
            win.destroy()

        okbtn = ttk.Button(win, text="OK", command=create)
        okbtn.pack(side="left", anchor="w", fill="x")
        cancelbtn = ttk.Button(win, text="Cancel", command=lambda: win.destroy())
        cancelbtn.pack(side="left", anchor="w", fill="x")
        win.mainloop()
        self.refresh_tree()

    def open_dir(self, _):
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

    def process_directory(self, parent, showdironly: bool = False, path: str = ""):
        if os.path.isfile(path):
            return
        items = sorted(os.listdir(path))
        if not items:
            self.tree.insert(parent, "end", text="Empty", tags=("empty",))
        last_dir_index = 0
        for p in items:
            abspath = os.path.join(path, p)
            isdir = os.path.isdir(abspath)
            if isdir:
                oid = self.tree.insert(
                    parent,
                    last_dir_index,
                    text=p,
                    tags="subfolder",
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
                    parent, "end", text=p, open=False, image=self.icons[-1]
                )

    def on_double_click_treeview(self, event, destroy: bool = False):
        tree = self.tree
        item = tree.identify("item", event.x, event.y)
        name = self.get_path(item, True)
        self.opencommand(name)
        if destroy:
            self.master.destroy()

    def get_parent(self, item):
        """Find the path to item in treeview"""
        tree = self.tree
        parent_iid = tree.parent(item)
        parent_text = tree.item(parent_iid, "text")
        self.temp_path.append(parent_text)
        if parent_text:
            self.get_parent(parent_iid)

    def get_path(self, item, append_name: bool = False):
        self.temp_path = []
        self.get_parent(item)
        self.temp_path.reverse()
        self.temp_path.remove("")
        if append_name:
            self.temp_path.append(self.tree.item(item, "text"))
        return os.path.abspath("/".join(self.temp_path))

    def right_click(self, event):
        menu = tk.Menu(self.master)
        item = self.tree.identify("item", event.x, event.y)
        is_path = False
        if not item:
            item = self.root_node
            is_path = True

        new_cascade = tk.Menu(menu)
        new_cascade.add_command(label="New File", command=lambda: self.new_file(event))
        new_cascade.add_command(
            label="New Directory", command=lambda: self.new_folder(event)
        )
        menu.add_cascade(menu=new_cascade, label="New...")
        menu.add_separator()
        menu.add_command(label="Get Info", command=lambda: self.get_info(item, is_path))
        menu.add_command(label="Move to Trash", command=lambda: self.remove(item))
        menu.add_separator()
        menu.add_command(label="Refresh", command=self.refresh_tree)

        menu.tk_popup(event.x_root, event.y_root)

    def refresh_tree(self):
        path = self.path
        self.tree.delete(*self.tree.get_children())
        ypos = self.yscroll.get()
        abspath = os.path.abspath(path)
        self.root_node = self.tree.insert("", "end", text=abspath, open=True)
        self.process_directory(self.root_node, path=abspath)
        self.yscroll.set(*ypos)
