from src.Dialog.codelistdialog import CodeListDialog
from src.Dialog.commondialog import AboutDialog
from src.Dialog.debugdialog import LogViewDialog
from src.Dialog.goto import Navigate
from src.Dialog.searchindir import SearchInDir
from src.Dialog.testdialog import TestDialog
from src.Dialog.textstyle import StyleWindow
from src.modules import tk, subprocess
from src.constants import logger


def create_menu(self) -> None:
    self.appmenu = tk.Menu(self.menubar, tearoff=0)
    self.appmenu.add_command(label="About PyPlus", command=lambda: AboutDialog(self.master))
    self.appmenu.add_cascade(label='Settings',
                             menu=self.settings_class.create_menu(self.open_file, self.master))
    self.appmenu.add_command(label='View log', command=lambda: LogViewDialog())
    self.appmenu.add_command(label="Exit Editor", command=self.quit_editor)
    self.appmenu.add_command(label="Restart app", command=self.restart)

    self.filemenu = tk.Menu(self.menubar, tearoff=False)
    self.filemenu.add_command(
        label="New...",
        command=self.filetree.new_file,
        image=self.new_icon,
        compound='left'
    )
    open_cascade = tk.Menu(self.filemenu, tearoff=False)
    open_cascade.add_command(
        label="Open File",
        command=lambda: self.open_file(),
        image=self.open_icon,
        compound='left'
    )
    open_cascade.add_command(
        label="Open File in Hex",
        command=lambda: self.open_hex(),
        image=self.open_icon,
        compound='left'
    )
    open_cascade.add_command(
        label="Open Folder/Project",
        command=lambda: self.open_dir(),
        image=self.open_icon,
        compound='left'
    )
    self.filemenu.add_cascade(label='Open...', menu=open_cascade)
    self.filemenu.add_command(
        label="Save Copy to...",
        command=lambda: self.save_as(),
        image=self.save_as_icon,
        compound='left'
    )
    self.filemenu.add_command(
        label="Close Tab",
        command=self.close_tab,
        image=self.close_icon,
        compound='left'
    )
    self.filemenu.add_command(
        label="Reload all files from disk",
        command=self.reload,
        image=self.reload_icon,
        compound='left'
    )
    editmenus = self.opts.create_menu(self.master)
    self.editmenu = editmenus[0]

    self.codemenu = self.codefuncs.create_menu(self.master)

    self.viewmenu = tk.Menu(self.menubar, tearoff=False)
    self.viewmenu.add_command(
        label="Unit tests",
        command=lambda: TestDialog(self.bottom_tabs, self.filetree.path),
    )
    self.viewmenu.add_command(label="Git: Commit and Push...", command=lambda: self.git("commit"))
    self.viewmenu.add_command(
        label="Classes and functions",
        command=lambda: CodeListDialog(self.panedwin,
                                       self.get_text()) if self.tabs else None
    )
    self.viewmenu.add_command(
        label='Insert Ascii Art',
        command=lambda: StyleWindow(self.get_text(), self.key) if self.tabs else None
    )
    self.viewmenu.add_command(
        label="Search In directory",
        command=lambda: SearchInDir(self.panedwin, self.filetree.path, self.open_file),
    )

    self.navmenu = tk.Menu(self.menubar, tearoff=False)
    self.navmenu.add_command(label="Go to ...",
                             command=lambda: Navigate(self.get_text()) if self.tabs else None)

    self.gitmenu = tk.Menu(self.menubar, tearoff=False)
    self.gitmenu.add_command(label="Initialize", command=lambda:
    subprocess.Popen(
        'git init && git add . && git commit -am "Added files"',
        shell=True,
        cwd=self.filetree.path,
    ))
    self.gitmenu.add_command(label="Clone...", command=lambda: self.git("clone"))

    self.menubar.add_cascade(label="PyPlus", menu=self.appmenu)  # App menu
    self.menubar.add_cascade(label="File", menu=self.filemenu)
    self.menubar.add_cascade(label="Edit", menu=self.editmenu)
    self.menubar.add_cascade(label="Code", menu=self.codemenu)
    self.menubar.add_cascade(label="View", menu=self.viewmenu)
    self.menubar.add_cascade(label="Navigate", menu=self.navmenu)
    self.menubar.add_cascade(label="Git", menu=self.gitmenu)

    self.master.config(menu=self.menubar)
    logger.debug("Menu created")
