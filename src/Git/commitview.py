from src.constants import APPDIR
from src.modules import lexers, os, subprocess, tk, ttk
from src.tktext import EnhancedTextFrame
from src.highlighter import create_tags, recolorize


class CommitView:
    def __init__(self, master, path):
        self.dir = path
        self.master = master
        subprocess.Popen("git add .", shell=True, cwd=self.dir)
        self.window = tk.Toplevel(self.master)
        self.window.title("Commit")
        self.window.resizable(0, 0)

        diff_frame = ttk.Frame(self.window)
        self.files_listbox = ttk.Treeview(diff_frame)
        self.refresh_files()

        self.files_listbox.pack(fill="both")
        self.files_listbox.tag_configure('added', foreground='green')
        self.files_listbox.tag_configure('modified', foreground='brown')
        self.files_listbox.tag_configure('deleted', foreground='red')
        self.files_listbox.bind('<1>', self.click_files)
        self.files_listbox.bind('<Double-1>', self.diff)
        diff_frame.pack(fill="both")

        commit_frame = ttk.Frame(self.window)
        commit_frame.pack(anchor="nw")
        self.committext = tk.Text(commit_frame, font="Arial", height=4)
        self.committext.pack()
        ttk.Button(commit_frame, text="Commit >>", command=self.commit).pack(
            side="bottom", fill="x"
        )
        self.window.mainloop()

    def click_files(self, _=None):
        item = self.files_listbox.focus()
        self.selected = self.files_listbox.item(item, "text")[2:]

    def commit(self, _=None):
        if commit_msg := self.committext.get("1.0", "end"):
            subprocess.Popen(
                f'git commit -am "{commit_msg}"',
                shell=True,
                cwd=self.dir,
            )
            self.window.destroy()

    def diff(self, _=None):
        try:
            diffwindow = tk.Toplevel(self.window)
            diffwindow.resizable(0, 0)
            textframe = EnhancedTextFrame(diffwindow)
            difftext = textframe.text
            difftext.lexer = lexers.get_lexer_by_name("diff")
            create_tags(difftext)
            recolorize(difftext)
            difftext.update()
            subprocess.Popen(
                f'git diff --staged {self.selected} > \
                            {os.path.join(APPDIR, "out.txt")}',
                shell=True,
                cwd=self.dir,
            )
            with open(os.path.join(APPDIR, "out.txt")) as f:
                message = f.read()
            os.remove("out.txt")
            difftext.insert("end", message)
            difftext.config(state="disabled", wrap="none")
            textframe.pack(fill="both")
            diffwindow.mainloop()
        except Exception as e:
            print(e, flush=True)

    def refresh_files(self):
        self.files_listbox.delete(*self.files_listbox.get_children())
        modified_files = [
            "M " + x
            for x in subprocess.Popen(
                "git diff --staged --name-only --diff-filter=M",
                stdout=subprocess.PIPE,
                shell=True,
                cwd=self.dir,
            )
            .communicate()[0]
            .decode("utf-8")
            .splitlines()
        ]
        renamed_files = [
            "R " + x
            for x in subprocess.Popen(
                "git diff --staged --name-only --diff-filter=R",
                stdout=subprocess.PIPE,
                shell=True,
                cwd=self.dir,
            )
            .communicate()[0]
            .decode("utf-8")
            .splitlines()
        ]
        added_files = [
            "A " + x
            for x in subprocess.Popen(
                "git diff --staged --name-only --diff-filter=A",
                stdout=subprocess.PIPE,
                shell=True,
                cwd=self.dir,
            )
            .communicate()[0]
            .decode("utf-8")
            .splitlines()
        ]
        deleted_files = [
            "D " + x
            for x in subprocess.Popen(
                "git diff --staged --name-only --diff-filter=D",
                stdout=subprocess.PIPE,
                shell=True,
                cwd=self.dir,
            )
            .communicate()[0]
            .decode("utf-8")
            .splitlines()
        ]
        copied_files = [
            "C " + x
            for x in subprocess.Popen(
                "git diff --staged --name-only --diff-filter=C",
                stdout=subprocess.PIPE,
                shell=True,
                cwd=self.dir,
            )
            .communicate()[0]
            .decode("utf-8")
            .splitlines()
        ]
        for x in added_files:
            self.files_listbox.insert(
                "",
                "end",
                text=x,
                tags='added'
            )
        for x in copied_files:
            self.files_listbox.insert(
                "",
                "end",
                text=x
            )
        for x in renamed_files:
            self.files_listbox.insert(
                "",
                "end",
                text=x
            )
        for x in deleted_files:
            self.files_listbox.insert(
                "",
                "end",
                text=x,
                tags='deleted'
            )
        for x in modified_files:
            self.files_listbox.insert(
                "",
                "end",
                text=x,
                tags='modified'
            )
