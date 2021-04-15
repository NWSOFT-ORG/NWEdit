from constants import APPDIR
from modules import lexers, os, subprocess, tk, ttk


class CommitView:
    def __init__(self, master, path):
        self.dir = path
        self.master = master
        subprocess.Popen("git add .", shell=True, cwd=self.dir)
        self.window = tk.Toplevel(self.master)
        self.window.title("Commit")
        self.window.resizable(0, 0)
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

        diff_frame = ttk.Frame(self.window)
        self.files_listbox = tk.Listbox(diff_frame)
        self.files_listbox.insert(
            "end",
            *added_files,
            *modified_files,
            *renamed_files,
            *copied_files,
            *deleted_files,
        )

        self.files_listbox.pack(fill="both")
        ttk.Button(diff_frame, text="Diff", command=self.diff).pack(side="left")
        diff_frame.pack(fill="both")

        commit_frame = ttk.Frame(self.window)
        commit_frame.pack(anchor="nw")
        self.committext = tk.Text(commit_frame, font="Arial", height=4)
        self.committext.pack()
        ttk.Button(commit_frame, text="Commit >>", command=self.commit).pack(
            side="bottom", fill="x"
        )
        self.window.mainloop()

    def commit(self, _=None):
        subprocess.Popen(
            f'git commit -am "{self.committext.get("1.0", "end")}"',
            shell=True,
            cwd=self.dir,
        )
        self.window.destroy()

    def diff(self, _=None):
        diffwindow = tk.Toplevel(self.window)
        diffwindow.resizable(0, 0)
        difftext = tk.Text(diffwindow, width=50, height=25)
        difftext.pack(fill="both", expand=1)
        difftext.lexer = lexers.get_lexer_by_name("diff")
        subprocess.Popen(
            f'git diff --staged {self.files_listbox.get(self.files_listbox.index("active"))[2:]} > \
                        {os.path.join(APPDIR, "out.txt")}',
            shell=True,
            cwd=self.dir,
        )
        with open(os.path.join(APPDIR, "out.txt")) as f:
            message = f.read()
        os.remove("out.txt")
        difftext.insert("end", message)
        difftext.config(state="disabled", wrap="none")
        diffwindow.mainloop()
