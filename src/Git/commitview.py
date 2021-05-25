from src.constants import APPDIR
from src.modules import lexers, os, subprocess, tk, ttk
from src.tktext import EnhancedTextFrame
from src.highlighter import create_tags, recolorize


class CommitView(ttk.Frame):
    def __init__(self, parent, path):
        super().__init__(parent)
        self.dir = path
        self.master = parent
        subprocess.run("git add .", shell=True, cwd=self.dir)

        diff_frame = ttk.Frame(self)
        self.files_listbox = ttk.Treeview(diff_frame, show="tree")

        self.files_listbox.pack(fill="both")
        self.files_listbox.tag_configure("added", foreground="green")
        self.files_listbox.tag_configure("modified", foreground="brown")
        self.files_listbox.tag_configure("deleted", foreground="red")
        self.files_listbox.bind("<<DoubleClick>>", self.diff)
        self.files_listbox.event_add("<<DoubleClick>>", "<Double-1>")
        diff_frame.pack(fill="both")

        commit_frame = ttk.Frame(self)
        commit_frame.pack(anchor="nw")
        self.committext = tk.Text(commit_frame, font="Arial", height=4)
        self.committext.pack()
        self.files_listbox.delete(*self.files_listbox.get_children())
        modified_files = [
            "M " + x
            for x in subprocess.run(
                "git diff --staged --name-only --diff-filter=M",
                capture_output=True,
                shell=True,
                cwd=self.dir,
            )
            .stdout.decode("utf-8")
            .splitlines()
        ]
        renamed_files = [
            "R " + x
            for x in subprocess.run(
                "git diff --staged --name-only --diff-filter=R",
                capture_output=True,
                shell=True,
                cwd=self.dir,
            )
            .stdout.decode("utf-8")
            .splitlines()
        ]
        added_files = [
            "A " + x
            for x in subprocess.run(
                "git diff --staged --name-only --diff-filter=A",
                capture_output=True,
                shell=True,
                cwd=self.dir,
            )
            .stdout.decode("utf-8")
            .splitlines()
        ]
        deleted_files = [
            "D " + x
            for x in subprocess.run(
                "git diff --staged --name-only --diff-filter=D",
                capture_output=True,
                shell=True,
                cwd=self.dir,
            )
            .stdout.decode("utf-8")
            .splitlines()
        ]
        copied_files = [
            "C " + x
            for x in subprocess.run(
                "git diff --staged --name-only --diff-filter=C",
                capture_output=True,
                shell=True,
                cwd=self.dir,
            )
            .stdout.decode("utf-8")
            .splitlines()
        ]
        for x in added_files:
            self.files_listbox.insert("", "end", text=x, tags="added")
        for x in copied_files:
            self.files_listbox.insert("", "end", text=x)
        for x in renamed_files:
            self.files_listbox.insert("", "end", text=x)
        for x in deleted_files:
            self.files_listbox.insert("", "end", text=x, tags="deleted")
        for x in modified_files:
            self.files_listbox.insert("", "end", text=x, tags="modified")

        ttk.Button(commit_frame, text="Commit >>", command=self.commit).pack(
            side="bottom", fill="x"
        )
        parent.forget(parent.panes()[0])
        parent.insert('0', self)
        self.pack(fill='both', expand=1)

    def commit(self, _=None):
        if commit_msg := self.committext.get("1.0", "end"):
            subprocess.Popen(
                f'git commit -am "{commit_msg}"',
                shell=True,
                cwd=self.dir,
            )
            self.destroy()

    def diff(self, event=None):
        item = self.files_listbox.identify("item", event.x, event.y)
        text = self.files_listbox.item(item, "text")
        prefix = text[0]
        selected = text[2:]
        diffwindow = tk.Toplevel(self)
        diffwindow.resizable(0, 0)
        diffwindow.title(f"Diff of {selected}")
        textframe = EnhancedTextFrame(diffwindow)
        difftext = textframe.text
        difftext.lexer = lexers.get_lexer_by_name("diff")
        difftext.update()
        subprocess.call(
            f'git diff --staged {selected} > \
                        {os.path.join(APPDIR, "out.txt")}',
            shell=True,
            cwd=self.dir,
        )
        with open(os.path.join(APPDIR, "out.txt")) as f:
            message = f.read()
        os.remove("out.txt")
        difftext.insert("end", message)
        create_tags(difftext)
        recolorize(difftext)
        difftext.config(state="disabled", wrap="none")
        textframe.pack(fill="both")
        diffwindow.mainloop()
