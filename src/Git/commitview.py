from src.modules import tk, ttk, subprocess, lexers, os
from src.tktext import EnhancedTextFrame
from src.constants import APPDIR
from src.highlighter import create_tags, recolorize


class CommitView(ttk.Frame):
    def __init__(self, parent, path: str):
        super().__init__(parent)
        self.parent = parent
        self.init_ui(parent)

        self.path = path
        subprocess.run("git add .", shell=True, cwd=self.path)

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
        ttk.Button(commit_frame, text="Commit >>", command=self.commit).pack(
            side="bottom", fill="x"
        )
        self.remote_selected = tk.StringVar()
        self.branch_selected = tk.StringVar()
        frame = ttk.Frame(self)

        self.remotes_list = ttk.Combobox(frame, textvariable=self.remote_selected)
        self.branches_list = ttk.Combobox(frame, textvariable=self.branch_selected)
        self.remotes_list.pack(side='left', anchor="nw")
        self.branches_list.pack(side='left', anchor="nw")
        self.remotes_list['state'] = 'readonly'
        self.branches_list['state'] = 'readonly'

        self.main_frame = ttk.LabelFrame(self, labelwidget=frame)
        self.main_frame.pack(fill='both', expand=1)

        self.name_label = ttk.Label(self.main_frame, text='')
        self.name_label.pack(fill='both', anchor='nw')

        self.push_button = ttk.Button(self.main_frame, text='Push', command=self.push)
        self.push_button.pack(anchor='nw', side='left')

        self.pull_button = ttk.Button(self.main_frame, text='Pull', command=self.pull)
        self.pull_button.pack(anchor='nw', side='left')

        remotes = [subprocess.run(
                "git remote",
                capture_output=True,
                shell=True,
                cwd=self.path,
                ).stdout.decode("utf-8").splitlines()]

        branches = [subprocess.run(
                "git branch -r --no-color",
                capture_output=True,
                shell=True,
                cwd=self.path,
                ).stdout.decode("utf-8").splitlines()]

        self.remotes_list["values"] = remotes
        self.remotes_list.set(remotes[0])
        self.branches_list["values"] = branches
        self.branches_list.set(branches[0])
        self.change_remote()
        self.update_filelist()
        self.remote_selected.trace_add('write', self.change_remote)
    
    def init_ui(self):
        parent = self.parent
        parent.forget(parent.panes()[0])
        self.pack(fill='both', expand=1)
        parent.insert('0', self)
    
    def update_filelist(self):
        modified_files = [
            "M " + x
            for x in subprocess.run(
                "git diff --staged --name-only --diff-filter=M",
                capture_output=True,
                shell=True,
                cwd=self.path,
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
                cwd=self.path,
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
                cwd=self.path,
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
                cwd=self.path,
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
                cwd=self.path,
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
            cwd=self.path,
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
    
    def pull(self):
        subprocess.Popen(f"git pull {self.current_remote}", shell=True)

    def push(self):
        subprocess.Popen(f"git push {self.current_remote}", shell=True)

    def change_remote(self, *_):
        self.current_remote  = self.remote_selected.get()
        name = subprocess.run(f"git config --get remote.{self.current_remote}.url", 
                              shell=True, cwd=self.path, capture_output=True
                              ).stdout.decode('utf-8')
        self.name_label.configure(text=name)