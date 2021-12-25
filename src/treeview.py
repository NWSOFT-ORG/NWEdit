from src.constants import APPDIR, OSX, WINDOWS, logger
from src.Dialog.commondialog import InputStringDialog, YesNoDialog, get_theme
from src.modules import os, shutil, time, tk, ttk, ttkthemes


class FileTree(ttk.Frame):
    """
    Treeview to select files
    """

    def __init__(
            self,
            master=None,
            opencommand=None,
            path=f'{APPDIR}/empty',
    ):
        self.temp_path = []
        style = ttk.Style()
        self._style = ttkthemes.ThemedStyle()
        self._style.set_theme(get_theme())
        self.bg = self._style.lookup("TLabel", "background")
        style.layout(
            "Treeview.Item",
            [
                (
                    "Treeitem.padding",
                    {
                        "sticky":   "nswe",
                        "children": [
                            ("Treeitem.indicator", {"side": "left", "sticky": ""}),
                            ("Treeitem.image", {"side": "left", "sticky": ""}),
                            ("Treeitem.text", {"side": "left", "sticky": ""}),
                        ],
                    },
                )
            ],
        )
        super().__init__(master)
        style.configure("style.Treeview", font=("Arial", 8))
        style.configure("style.Treeview.Heading", font=("Arial", 13, "bold"))
        self.tree = ttk.Treeview(self, style="style.Treeview", show='tree')
        self.yscroll = ttk.Scrollbar(self, command=self.tree.yview)
        self.xscroll = ttk.Scrollbar(
            self, command=self.tree.xview, orient="horizontal"
        )
        style.configure("style.Treeview", rowheight=25, background=self.bg)
        self.yscroll.pack(side="right", fill="y")
        self.xscroll.pack(side="bottom", fill="x")
        self.tree["yscrollcommand"] = self.yscroll.set
        self.tree["xscrollcommand"] = self.xscroll.set
        self.master = master
        self.path = path if path != "" else os.path.expanduser("~")
        self.opencommand = opencommand

        self.pack(side="left", fill="both", expand=1)
        self.refresh_tree()
        self.tree.bind("<Double-1>", self.on_double_click_treeview)
        self.tree.bind('<3>', self.right_click)
        self.tree.update()
        self.tree.tag_configure("row", font="Arial 10")
        self.tree.tag_configure("subfolder", foreground="#448dc4", font="Arial 10")
        self.tree.pack(fill="both", expand=1, anchor="nw")
        self.tree.bind('<<TreeviewOpen>>', self.open_dir)

    def get_path(self, event):
        return os.path.join(self.path, self.tree.item(self.tree.identify('item', event.x, event.y), "text"))

    def remove(self, event):
        path = self.get_path(event)
        if YesNoDialog(
                title="Warning!", text="This file/directory will be deleted immediately!"
        ):
            if os.path.isdir(path):
                shutil.rmtree(path)
            else:
                os.remove(path)
            self.refresh_tree()

    def rename(self, event):
        try:
            path = self.get_path(event)
            dialog = InputStringDialog(self.master, "Rename", "New name:")
            newdir = os.path.join(self.path, dialog.result)
            shutil.move(path, newdir)
            self.refresh_tree()
        except (IsADirectoryError, FileExistsError):
            pass

    def get_info(self, event):
        path = self.get_path(event)
        basename = os.path.basename(path)
        size = str(os.path.getsize(path))
        # Determine the correct unit
        if int(size) / 1024 < 1:
            size += "Bytes"
        elif int(size) / 1024 >= 1 <= 2:
            size = f"{int(size) // 1024} Kilobytes"
        elif int(size) / 1024 ** 2 >= 1 <= 2:
            size = f"{int(size) // 1024 ** 2} Megabytes"
        elif int(size) / 1024 ** 3 >= 1 <= 2:
            size = f"{int(size) // 1024 ** 3} Gigabytes"
        elif int(size) / 1024 ** 4 >= 1 <= 2:
            size = f"{int(size) // 1024 ** 4} Terrabytes"
        # It can go on and on, but the newest PCs won't have more than a PB storage
        #      /-------------/|
        #     /			    / /
        #    /  SSD		   / /
        #   /   10 TB  	  / /
        #  /	    	 / /
        # /             / /
        # \=============\/
        mdate = f"Last modified: {time.ctime(os.path.getmtime(path))}"
        cdate = f"Created: {time.ctime(os.path.getctime(path))}"
        win = tk.Toplevel(master=self.master)
        win.title(f"Info of {basename}")
        win.resizable(0, 0)
        win.transient(".")
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
        win.title("New Directory")
        win.transient(".")
        win.resizable(0, 0)
        win.config(background=self.bg)
        ttk.Label(win, text="Name:").pack(side="top", anchor="nw")
        filename = tk.Entry(win)
        filename.pack(side="top", anchor="nw")
        item = self.tree.item(self.tree.identify('item', event.x, event.y), 'text')

        def create():
            if not filename.get():
                return
            path = f'{item}/{filename.get()}'
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
        win = tk.Toplevel(self.master)
        win.title("New File")
        win.transient(".")
        win.resizable(0, 0)
        win.config(background=self.bg)
        ttk.Label(win, text="Name:").pack(side="top", anchor="nw")
        filename = tk.Entry(win)
        filename.pack(side="top", anchor="nw")
        try:
            item = self.tree.item(self.tree.parent(self.tree.identify('item', event.x, event.y)), "text")
        except AttributeError:
            item = self.tree.item(self.tree.parent(self.tree.focus()), "text")

        def create():
            if not filename.get():
                return
            path = f'{item}/{filename.get()}'
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
        tree = self.tree
        item = tree.focus()
        item_text = tree.item(item, 'text')
        self.temp_path = []
        self.get_parent(item)
        path = f'{"/".join(reversed(self.temp_path))[1:]}/{item_text}'
        if os.path.isfile(path):
            return
        self.path = path
        logger.debug(f'Opened tree item, path: {self.path}')
        tree.delete(*tree.get_children(item))
        self.process_directory(item, path=self.path)

    def process_directory(self, parent, showdironly: bool = False, path: str = ''):
        if os.path.isfile(path):
            return
        items = sorted(os.listdir(path))
        last_dir_index = 0
        for p in items:
            abspath = os.path.join(path, p)
            isdir = os.path.isdir(abspath)
            if isdir:
                oid = self.tree.insert(parent, last_dir_index, text=p, tags='subfolder', open=False)
                last_dir_index += 1
                if not showdironly:
                    self.tree.insert(oid, 0, text='Loading...')
            else:
                self.tree.insert(parent, 'end', text=p, tags='row', open=False)

    def on_double_click_treeview(self, event, destroy: bool = False):
        tree = self.tree
        item = tree.identify('item', event.x, event.y)
        name = tree.item(item, 'text')
        self.temp_path = []
        self.get_parent(item)
        self.temp_path.reverse()
        self.temp_path.remove('')
        self.temp_path = os.path.abspath('/'.join(self.temp_path))
        self.opencommand(os.path.join(self.temp_path, name))

    def get_parent(self, item):
        """Find the path to item in treeview"""
        tree = self.tree
        parent_iid = tree.parent(item)
        parent_text = tree.item(parent_iid, 'text')
        self.temp_path.append(parent_text)
        if parent_text:
            self.get_parent(parent_iid)

    def right_click(self, event):
        menu = tk.Menu(self.master)

        new_cascade = tk.Menu(menu)
        new_cascade.add_command(label='New File', command=lambda: self.new_file(event))
        new_cascade.add_command(label='New Directory', command=lambda: self.new_folder(event))
        menu.add_cascade(menu=new_cascade, label='New...')
        menu.add_separator()
        menu.add_command(label='Refresh', command=self.refresh_tree)

        menu.tk_popup(event.x_root, event.y_root)

    def refresh_tree(self):
        path = self.path
        self.tree.delete(*self.tree.get_children())
        ypos = self.yscroll.get()
        self.tree.heading("#0", text=path)
        abspath = os.path.abspath(path)
        root_node = self.tree.insert('', 'end', text=abspath, tags='row', open=True)
        self.process_directory(root_node, path=abspath)
        self.yscroll.set(*ypos)

