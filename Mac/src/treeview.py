from src.constants import OSX, WINDOWS
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
        path=os.path.expanduser("~"),
    ):
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
                        "sticky": "nswe",
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

    def remove(self):
        path = os.path.join(self.path, self.tree.item(self.tree.focus())["text"])
        if YesNoDialog(
            title="Warning!", text="This file/directory will be deleted immediately!"
        ):
            if os.path.isdir(path):
                shutil.rmtree(path)
            else:
                os.remove(path)
            self.refresh_tree()

    def rename(self):
        try:
            path = os.path.join(self.path, self.tree.item(self.tree.focus())["text"])
            dialog = InputStringDialog(self.master, "Rename", "New name:")
            newdir = os.path.join(self.path, dialog.result)
            shutil.move(path, newdir)
            self.refresh_tree()
        except (IsADirectoryError, FileExistsError):
            pass

    def get_info(self):
        path = os.path.join(self.path, self.tree.item(self.tree.focus())["text"])
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
                text="Note: the dates would not be the exact date of creation or modification!",
            ).pack(side="top", anchor="nw", fill="x")
        win.mainloop()
    
    def new_folder(self, item):
        win = tk.Toplevel(master=self.master)
        win.title("New Directory")
        win.transient(".")
        win.resizable(0, 0)
        win.config(background=self.bg)
        ttk.Label(win, text="Name:").pack(side="top", anchor="nw")
        filename = tk.Entry(win)
        filename.pack(side="top", anchor="nw")
        def create():
            if not filename.get():
                return
            path = []
            tree = self.tree
            def get_parent(item):
                parent_iid = tree.parent(item)
                parent_text = tree.item(parent_iid, 'text')
                path.append(parent_text)
                if parent_text:
                    get_parent(parent_iid)

            path = '/'.join(path)
            try:
                os.mkdir(path)
            except FileExistsError:
                if YesNoDialog(
                    title="This directory already exsists!",
                    text="Do you want to overwrite?",
                ).result:
                    shutil.rmtree(path, ignore_errors=True)
                    os.mkdir(path)

    def new_file(self, item):
        print(item)
        win = tk.Toplevel(master=self.master)
        win.title("New File")
        win.transient(".")
        win.resizable(0, 0)
        win.config(background=self.bg)
        ttk.Label(win, text="Name:").pack(side="top", anchor="nw")
        filename = tk.Entry(win)
        filename.pack(side="top", anchor="nw")
        def create():
            if not filename.get():
                return
            tree = self.tree
            path = []

            def get_parent(item):
                parent_iid = tree.parent(item)
                parent_text = tree.item(parent_iid, 'text')
                path.append(parent_text)
                if parent_text:
                    get_parent(parent_iid)

            path = path[1:]
            path = '/'.join(path)
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

    def process_directory(self, parent, showdironly: bool = False, path: str = ''):
        items = os.listdir(path)
        last_dir_index = 0
        for p in items:
            abspath = os.path.join(path, p)
            isdir = os.path.isdir(abspath)
            if isdir:
                oid = self.tree.insert(parent, last_dir_index, text=p, tags='subfolder', open=False)
                last_dir_index += 1
                self.process_directory(oid, path=abspath)
            else:
                oid = self.tree.insert(parent, 'end', text=p, tags='row', open=False)

    def on_double_click_treeview(self, event, destroy: bool = False):
        global path
        tree = self.tree
        item = tree.identify('item', event.x, event.y)
        name = tree.item(item, 'text')
        path = []

        def get_parent(item):
            parent_iid = tree.parent(item)
            parent_text = tree.item(parent_iid, 'text')
            path.append(parent_text)
            if parent_text:
                get_parent(parent_iid)

        get_parent(item)
        path.reverse()
        path.remove('')
        path = os.path.abspath('/'.join(path))
        self.opencommand(os.path.join(path, name))
    
    def right_click(self, event):
        item = self.tree.identify('item', event.x, event.y)
        
        menu = tk.Menu(self.master)

        new_cascade = tk.Menu(menu)
        new_cascade.add_command(label='New File', command=lambda: self.new_file(item))
        new_cascade.add_command(label='New Directory', command=lambda: self.new_folder(item))
        menu.add_cascade(menu=new_cascade, label='New...')
        
        menu.tk_popup(event.x_root, event.y_root)

    def refresh_tree(self):
        self.tree.delete(*self.tree.get_children())
        ypos = self.yscroll.get()
        self.tree.heading("#0", text=self.path)
        path = self.path
        abspath = os.path.abspath(path)
        root_node = self.tree.insert('', 'end', text=abspath, tags='row', open=True)
        self.process_directory(root_node, path=abspath)
        self.yscroll.set(*ypos)
