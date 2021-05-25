from src.modules import tk, ttk, subprocess


class RemoteView(ttk.Frame):
    def __init__(self, parent, path: str):
        super().__init__(parent)
        self.path = path
        
        self.remote_selected = tk.StringVar()
        self.remotes_list = ttk.Combobox(self, textvariable=self.remote_selected)
        self.remotes_list['state'] = 'readonly'
        self.main_frame = ttk.LabelFrame(self, labelwidget=self.remotes_list)
        self.main_frame.pack(fill='both', expand=1)
        self.name_label = ttk.Label(self.main_frame, text='')
        self.name_label.pack(fill='both', anchor='nw')
        self.push_button = ttk.Button(self.main_frame, text='Push', command=self.push)
        self.push_button.pack()
        self.pull_button = ttk.Button(self.main_frame, text='Pull', command=self.pull)
        self.pull_button.pack()

        remotes = subprocess.run(
                "git remote",
                capture_output=True,
                shell=True,
                cwd=self.path,
                ).stdout.decode("utf-8").splitlines()
        self.remotes_list["values"] = remotes
        parent.forget(parent.panes()[0])
        parent.insert('0', self)
        self.pack(fill='both', expand=1)

        self.remote_selected.trace_add('write', self.change_remote)
    
    def pull(self):
        subprocess.Popen(f"git pull {self.current_remote}", shell=True)

    def push(self):
        subprocess.Popen(f"git push {self.current_remote}", shell=True)

    def change_remote(self, *_):
        self.current_remote  = self.remote_selected.get()
        name = subprocess.run(f"git config --get remote.{self.current_remote}.url", 
                              shell=True, cwd=self.path, capture_output=True
                              ).stdout.decode('utf-8')