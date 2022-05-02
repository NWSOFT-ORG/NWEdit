from src.constants import logger
from src.Dialog.codelistdialog import CodeListDialog
from src.Dialog.commondialog import AboutDialog
from src.Dialog.debugdialog import LogViewDialog
from src.Dialog.goto import Navigate
from src.Dialog.searchindir import SearchInDir
from src.Dialog.testdialog import TestDialog
from src.Dialog.textstyle import StyleWindow
from src.modules import subprocess, tk
from src.Utils.images import get_image


def create_menu(self) -> None:
    self.appmenu = tk.Menu(self.menubar, name="apple")
    self.appmenu.add_command(
        label="About PyPlus", command=lambda: AboutDialog(self.master)
    )
    self.appmenu.add_cascade(
        label="Settings",
        menu=self.settings_class.create_menu(self.open_file, self.master),
    )
    self.appmenu.add_command(
        label="View log", command=lambda: LogViewDialog(self.master)
    )
    self.appmenu.add_command(label="Exit Editor", command=self.exit)
    self.appmenu.add_command(label="Restart app", command=self.restart)

    self.filemenu = tk.Menu(self.menubar)
    self.filemenu.add_command(
        label="New...",
        command=self.filetree.new_file,
        image=get_image("new"),
        compound="left",
    )
    open_cascade = tk.Menu(self.filemenu)
    open_cascade.add_command(
        label="Open File",
        command=lambda: self.open_file(),
        image=get_image("open"),
        compound="left",
    )
    open_cascade.add_command(
        label="Open File in Hex",
        command=lambda: self.open_hex(),
        image=get_image("open"),
        compound="left",
    )
    open_cascade.add_command(
        label="Open Folder/Project",
        command=lambda: self.open_dir(),
        image=get_image("open"),
        compound="left",
    )
    self.filemenu.add_cascade(label="Open...", menu=open_cascade)
    self.filemenu.add_command(
        label="Save Copy to...",
        command=lambda: self.save_as(),
        image=get_image("saveas"),
        compound="left",
    )
    self.filemenu.add_command(
        label="Close Tab",
        command=self.close_tab,
        image=get_image("close"),
        compound="left",
    )
    self.filemenu.add_command(
        label="Reload all files from disk",
        command=self.reload,
        image=get_image("reload"),
        compound="left",
    )
    self.editmenu = self.opts.create_menu[0]

    self.codemenu = self.codefuncs.create_menu

    self.viewmenu = tk.Menu(self.menubar)
    self.viewmenu.add_command(
        label="Unit tests",
        command=lambda: TestDialog(self.bottom_tabs, self.filetree.path),
    )
    self.viewmenu.add_command(
        label="Git: Commit and Push...", command=lambda: self.git("commit")
    )
    self.viewmenu.add_command(
        label="Classes and functions",
        command=lambda: CodeListDialog(self.bottom_tabs, self.get_text)
        if self.tabs
        else None,
    )
    self.viewmenu.add_command(
        label="Insert Ascii Art",
        command=lambda: StyleWindow(self.master, self.get_text, self.key)
        if self.tabs
        else None,
    )
    self.viewmenu.add_command(
        label="Search In directory",
        command=lambda: SearchInDir(self.bottom_tabs, self.filetree.path, self.open_file),
    )

    self.navmenu = tk.Menu(self.menubar)
    self.navmenu.add_command(
        label="Go to ...",
        command=lambda: Navigate(self.get_text) if self.tabs else None,
    )

    self.gitmenu = tk.Menu(self.menubar)
    self.gitmenu.add_command(
        label="Initialize",
        command=lambda: subprocess.Popen(
            'git init && git add . && git commit -am "Added files"',
            shell=True,
            cwd=self.filetree.path,
        ),
    )
    self.gitmenu.add_command(label="Clone...", command=lambda: self.git("clone"))

    self.menubar.add_cascade(label="PyPlus", menu=self.appmenu)  # App menu
    self.menubar.add_cascade(label="File", menu=self.filemenu)
    self.menubar.add_cascade(label="Edit", menu=self.editmenu)
    self.menubar.add_cascade(label="Code", menu=self.codemenu)
    self.menubar.add_cascade(label="View", menu=self.viewmenu)
    self.menubar.add_cascade(label="Navigate", menu=self.navmenu)
    self.menubar.add_cascade(
        label="Tools", menu=self.plugins_settings_class.create_tool_menu
    )
    self.menubar.add_cascade(label="Git", menu=self.gitmenu)

    self.master.config(menu=self.menubar)
    logger.debug("Menu created")
