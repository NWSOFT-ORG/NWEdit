from modules import *
from constants import *


class FileTree(ttk.Frame):
    """
        Treeview to select files
    """

    def __init__(self, master=None, opencommand=None, path=os.path.expanduser('~')):
        super().__init__(master)
        self.destinationItem = None
        self.sourceItem = None
        self.tree = ttk.Treeview(self)
        yscroll, xscroll = ttk.Scrollbar(self, command=self.tree.yview), \
                           ttk.Scrollbar(self, command=self.tree.xview, orient='horizontal')
        yscroll.pack(side='right', fill='y')
        xscroll.pack(side='bottom', fill='x')
        self.tree['yscrollcommand'] = yscroll.set
        self.tree['xscrollcommand'] = xscroll.set
        self.dir = ''
        self.selected = []
        self.master = master
        self.path = str(path)
        self.opencommand = opencommand
        topframe = ttk.Frame(self)
        topframe.pack(side='top', anchor='nw')
        self.actioncombobox = ttk.Combobox(topframe, state='readonly',
                                           values=['Parent Directory', 'New...', 'Refresh',
                                                   'Remove...', 'Get info...'])
        self.actioncombobox.set('Parent Directory')
        self.actioncombobox.pack(anchor='nw', side='left')
        ttk.Button(topframe, text='>>', command=self.do_action).pack(side='left', anchor='nw')

        self.pack(side='left', fill='both', expand=1)
        self.init_ui()
        self.tree.tag_configure('row', background='black', foreground='white')
        self.tree.tag_configure('folder', background='black', foreground='yellow')
        self.tree.tag_configure('subfolder', background='black', foreground='#448dc4')

    def do_action(self):
        action = self.actioncombobox.get()
        if action == 'Parent Directory':
            self.change_parent_dir()
        elif action == 'New...':
            self.new_file()
        elif action == 'Refresh':
            self.init_ui()
        elif action == 'Remove...':
            self.remove()
        elif action == 'Get info...':
            self.get_info()

    def remove(self):
        path = os.path.join(self.path, self.tree.item(self.tree.focus())['text'])
        if messagebox.askyesno('Warning!', 'This file/directory will be deleted immediately!'):
            if os.path.isdir(path):
                shutil.rmtree(path)
            else:
                os.remove(path)
            self.init_ui()
    
    def get_info(self):
        path = os.path.join(self.path, self.tree.item(self.tree.focus())['text'])
        basename = os.path.basename(path)
        size = str(os.path.getsize(path))
        if int(size) / 1024 < 1:
            size += 'Bytes'
        elif int(size) / 1024 >= 1 <= 2:
            size = f'{int(size) // 1024} Kilobytes'
        elif int(size) / 1024 ** 2 >= 1 <= 2:
            size = f'{int(size) // 1024 ** 2} Megabytes'
        elif int(size) / 1073.741824 >= 1 <= 2:
            size = f'{int(size) // 1024 ** 2} Gigabytes'
        elif int(size) / 1099.511627776 >= 1 <= 2:
            size = f'{int(size) // 1024 ** 2} Terrabytes'
        # It can go on and on, but the newest PCs won't have more than a PB storage!
        mdate = f"Last modified: {time.ctime(os.path.getmtime(path))}"
        cdate = f"Created: {time.ctime(os.path.getctime(path))}"
        win = tk.Toplevel(master=self.master)
        win.title(f'Info of {basename}')
        win.resizable(0, 0)
        win.transient('.')
        ttk.Label(win, text=f'Name: {basename}').pack(side='top', anchor='nw', fill='x')
        ttk.Label(win, text=f'Path: {path}').pack(side='top', anchor='nw', fill='x')
        ttk.Label(win, text=f'Size: {size}').pack(side='top', anchor='nw', fill='x')
        ttk.Label(win, text=mdate).pack(side='top', anchor='nw', fill='x')
        ttk.Label(win, text=cdate).pack(side='top', anchor='nw', fill='x')
        if not WINDOWS or OSX:
            ttk.Label(win,
                      text='Note: the dates would not be the exact date of creation or modification!')\
            .pack(side='top', anchor='nw', fill='x')
        win.mainloop()

    def new_file(self):
        global _type
        win = tk.Toplevel(master=self.master)
        win.title('New File/Directory')
        win.transient('.')
        win.resizable(0, 0)
        filename = tk.Entry(win)
        filename.pack()
        _type = tk.IntVar()
        _type.set(1)

        def select(_=None):
            _type.set(not _type.get())

        _dir = ttk.Radiobutton(win, value=1, text='Directory', command=select)
        _dir.pack(side='left')
        _file = ttk.Radiobutton(win, value=0, text='File', command=select)
        _file.pack(side='left')

        def create(_=None):
            path = os.path.join(self.path, filename.get())
            if not _type:
                try:
                    os.mkdir(path)
                except FileExistsError:
                    if messagebox.askyesno('This directory already exsists!', 'Do you want to overwrite?'):
                        shutil.rmtree(path, ignore_errors=True)
                        os.mkdir(path)
            else:
                if os.path.exists(path):
                    if messagebox.askyesno('This file already exsists!', 'Do you want to overwrite?'):
                        with open(path, 'w') as f:
                            f.write('')
                        self.opencommand(path)
                else:
                    with open(path, 'w') as f:
                        f.write('')
                    self.opencommand(path)
            self.init_ui()

        okbtn = ttk.Button(win, text='OK', command=create)
        okbtn.pack()
        cancelbtn = ttk.Button(win, text='Cancel', command=lambda _=None: win.destroy())
        cancelbtn.pack()
        win.mainloop()

    def init_ui(self, _=None):
        path = os.path.expanduser('~')
        path_list = path.split('/')[:-1]
        for item in path_list:
            self.dir += item + '/'

        self.tree.delete(*self.tree.get_children())
        self.tree.bind("<Double-1>", self.on_double_click_treeview)
        self.tree.heading('#0', text='Directory Structure')
        self.tree.update()

        abspath = os.path.abspath(path)
        root_node = self.tree.insert('', 'end', text=abspath, open=True, tags='folder')
        self.process_directory(root_node, abspath)

        self.tree.pack(side='bottom', expand=True, fill='both', anchor='nw')

        self.refresh_tree()

    def change_parent_dir(self):
        self.path = str(Path(os.path.abspath(self.path)).parent)
        self.refresh_tree()

    def process_directory(self, parent, path):
        ls = os.listdir(path)
        dirs = []
        files = []
        for file in ls:
            if os.path.isdir(os.path.join(self.path, file)):
                dirs.append(file)
            else:
                files.append(file)

        for item in sorted(dirs):
            self.tree.insert(parent, 'end', text=str(item), open=False, tags='subfolder')

        for item in sorted(files):
            self.tree.insert(parent, 'end', text=str(item), open=False, tags='row')

    def on_double_click_treeview(self, event):
        try:
            item = self.tree.identify('item', event.x, event.y)
            tags = self.tree.item(item, "tags")[0]
            if tags == 'subfolder':
                root = self.path
                sub = self.tree.item(item, "text")
                _dir = os.path.join(root, sub)
                self.path = _dir
                self.refresh_tree()

            elif tags == 'folder':
                self.refresh_tree()
                return

            else:
                file = self.tree.item(item, "text")
                _dir = self.path
                _dir = self.check_path(_dir)
                _filename = os.path.join(_dir, file)
                self.selected = []
                try:
                    self.opencommand(_filename)
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

    @staticmethod
    def check_path(path):
        if '\\' in path:
            path = path.replace('\\', '/')
        return path

    def refresh_tree(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        path = self.path
        abspath = os.path.abspath(path)
        root_node = self.tree.insert('', 'end', text=abspath, open=True, tags='folder')
        self.process_directory(root_node, abspath)
