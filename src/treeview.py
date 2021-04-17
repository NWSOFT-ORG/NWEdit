from constants import OSX, WINDOWS
from dialogs import InputStringDialog, YesNoDialog
from modules import os, shutil, time, tk, ttk


class FileTree(ttk.Frame):
    """
    Treeview to select files
    """

    def __init__(
        self,
        master=None,
        opencommand=None,
        path=os.path.expanduser("~"),
        showbuttonframe: bool = True,
    ):
        super().__init__(master)
        style = ttk.Style()
        style.configure("style.Treeview", font=('Arial', 11))
        style.configure("style.Treeview.Heading", font=('Arial', 13,'bold'))
        style.configure('style.Treeview', rowheight=25)
        self.tree = ttk.Treeview(self, style="style.Treeview")
        yscroll, xscroll = ttk.Scrollbar(self, command=self.tree.yview), ttk.Scrollbar(
            self, command=self.tree.xview, orient="horizontal"
        )
        yscroll.pack(side="right", fill="y")
        xscroll.pack(side="bottom", fill="x")
        self.tree["yscrollcommand"] = yscroll.set
        self.tree["xscrollcommand"] = xscroll.set
        self.master = master
        self.path = str(path)
        self.opencommand = opencommand
        if showbuttonframe:
            topframe = ttk.Frame(self)
            topframe.pack(side="top", anchor="nw")
            self.actioncombobox = ttk.Combobox(
                topframe,
                state="readonly",
                values=["Rename...", "New...", "Refresh", "Remove...", "Get info..."],
            )
            self.actioncombobox.set("New...")
            self.actioncombobox.pack(anchor="nw", side="left")
            ttk.Button(topframe, text=">>", command=self.do_action).pack(
                side="left", anchor="nw"
            )

        self.pack(side="left", fill="both", expand=1)
        self.init_ui()
        self.tree.tag_configure("row", foreground="white", font='Arial 10')
        self.tree.tag_configure("subfolder", foreground="#448dc4", font='Arial 10')
        self.tree.pack(fill="both", expand=1, anchor="nw")

    def do_action(self):
        action = self.actioncombobox.get()
        if action == "New...":
            self.new_file()
        elif action == "Rename...":
            self.rename()
        elif action == "Refresh":
            self.init_ui()
        elif action == "Remove...":
            self.remove()
        elif action == "Get info...":
            self.get_info()

    def remove(self):
        path = os.path.join(self.path, self.tree.item(self.tree.focus())["text"])
        if YesNoDialog(
            title="Warning!", text="This file/directory will be deleted immediately!"
        ):
            if os.path.isdir(path):
                shutil.rmtree(path)
            else:
                os.remove(path)
            self.init_ui()

    def rename(self):
        try:
            path = os.path.join(self.path, self.tree.item(self.tree.focus())["text"])
            dialog = InputStringDialog(self.master, "Rename", "New name:")
            newdir = os.path.join(self.path, dialog.result)
            os.rename(path, newdir)
            self.init_ui()
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

    def new_file(self, _=None):
        global _type
        win = tk.Toplevel(master=self.master)
        win.title("New File/Directory")
        win.transient(".")
        win.resizable(0, 0)
        ttk.Label(win, text="Name:").pack(side="top", anchor="nw")
        filename = tk.Entry(win)
        filename.pack(side="top", anchor="nw")
        ttk.Label(win, text="Type:").pack(anchor="nw")
        _type = ttk.Combobox(win, values=["Directory", "File"], state="readonly")
        _type.pack(side="top", anchor="nw")
        _type.set("File")

        def create(_=None):
            if not filename.get():
                return
            path = os.path.join(self.path, filename.get())
            if _type.get() == "Directory":
                try:
                    os.mkdir(path)
                except FileExistsError:
                    if YesNoDialog(
                        title="This directory already exsists!",
                        text="Do you want to overwrite?",
                    ).result:
                        shutil.rmtree(path, ignore_errors=True)
                        os.mkdir(path)
            else:
                if os.path.exists(path):
                    if YesNoDialog(
                        title="This file already exsists!",
                        text="Do you want to overwrite?",
                    ).result:
                        with open(path, "w") as f:
                            f.write("")
                        self.opencommand(path)
                else:
                    with open(path, "w") as f:
                        f.write("")
                    self.opencommand(path)
            self.init_ui()
            win.destroy()

        okbtn = ttk.Button(win, text="OK", command=create)
        okbtn.pack(side="left", anchor="w", fill="x")
        cancelbtn = ttk.Button(win, text="Cancel", command=lambda _=None: win.destroy())
        cancelbtn.pack(side="left", anchor="w", fill="x")
        win.mainloop()
        self.init_ui()

    def init_ui(self):
        path = os.path.expanduser("~")

        self.tree.delete(*self.tree.get_children())
        self.tree.bind("<Double-1>", self.on_double_click_treeview)
        self.tree.update()

        abspath = os.path.abspath(path)
        self.process_directory(abspath)

        self.refresh_tree()

    def process_directory(self, path: str, showdironly: bool = False):
        ls = os.listdir(path)
        dirs = []
        files = []
        for file in ls:
            if os.path.isdir(os.path.join(self.path, file)):
                dirs.append(file)
            else:
                files.append(file)
        dirs.append("..")

        for item in sorted(dirs):
            self.tree.insert("", "end", text=str(item), open=False, tags="subfolder")

        if not showdironly:
            for item in sorted(files):
                self.tree.insert("", "end", text=str(item), open=False, tags="row")

    def on_double_click_treeview(self, _=None, destroy: bool = False):
        try:
            item = self.tree.focus()
            tags = self.tree.item(item, "tags")[0]
            if tags == "subfolder":
                root = self.path
                sub = self.tree.item(item, "text")
                _dir = os.path.join(root, sub)
                self.path = os.path.abspath(_dir)
                self.refresh_tree()
                self.tree.update()

            else:
                file = self.tree.item(item, "text")
                _dir = self.path
                _filename = os.path.join(_dir, file)
                try:
                    self.opencommand(_filename)
                    if destroy:
                        self.master.destroy()
                except Exception:
                    pass

                self.tree.update()

                # workaround
                # step 2
                self.refresh_tree()
                self.tree.update()

            self.refresh_tree()
        except Exception:
            pass

    def refresh_tree(self):
        self.tree.delete(*self.tree.get_children())
        self.tree.heading("#0", text=self.path)
        path = self.path
        abspath = os.path.abspath(path)
        self.process_directory(abspath)
