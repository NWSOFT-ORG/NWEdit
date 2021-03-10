from modules import *


class FileTree(ttk.Frame):
    """
        LeftPanel ... containing treeView, leftButtonFrame, Buttons
    """

    def __init__(self, master=None, textbox=None, opencommand=None, path=None):
        super().__init__(master)
        self.selected = []
        self.destinationItem = None
        self.sourceItem = None
        self.tree = ttk.Treeview(self, show='tree')
        self.dir = ''
        self.master = master
        self.textbox = textbox
        self.path = str(path)
        self.opencommand = opencommand
        topframe = ttk.Frame(self)
        topframe.pack(side='top', anchor='nw')
        self.actioncombobox = ttk.Combobox(topframe, state='readonly',
                                           values=['Parent Directory', 'New File'])
        self.actioncombobox.set('Parent Directory')
        self.actioncombobox.pack(anchor='nw', side='left')
        ttk.Button(topframe, text='>>', command=self.do_action).pack(side='left', anchor='nw')

        self.pack(side='left', fill='both', expand=1)
        self.initUI()
        self.tree.tag_configure('row', background='black', foreground='white')
        self.tree.tag_configure('folder', background='black', foreground='yellow')
        self.tree.tag_configure('subfolder', background='black', foreground='#448dc4')

    def do_action(self):
        action = self.actioncombobox.get()
        if action == 'Parent Directory':
            self.change_parent_dir()
        elif action == 'New File':
            self.new_file()

    def new_file(self):
        filename = simpledialog.askstring('New file', 'File Name:')
        file_abspath = os.path.join(self.path, filename)
        with open(file_abspath, 'w') as f:
            f.write('')
        self.opencommand(file_abspath)

    def new_dir(self):
        dirname = simpledialog.askstring('New directory', 'Directory Name:')
        dir_abspath = os.path.join(self.path, dirname)
        os.mkdir(dir_abspath)

    def initUI(self):
        path = os.path.abspath(__file__)
        path_list = path.split('/')[:-1]
        for item in path_list:
            self.dir += item + '/'

        left_button_frame = ttk.Frame(self, height=25)
        left_button_frame.pack(side=tk.TOP, fill=tk.X)

        os.chdir(self.path)
        self.tree.bind("<Double-1>", self.on_double_click_treeview)
        self.tree.bind('<<TreeviewSelect>>', self.on_select)
        self.tree.bind('<Alt-Right>', self.change_to_textbox)
        self.tree.heading('#0', text='Directory Structure')
        self.tree.update()

        abspath = os.path.abspath(path)
        root_node = self.tree.insert('', 'end', text=abspath, open=True, tags='folder')
        self.process_directory(root_node, abspath)

        self.tree.pack(side='bottom', expand=True, fill='both', anchor='nw')

        self.refreshTree()

    def change_to_textbox(self, _=None):
        if self.textbox:
            self.textbox.focus_set()

    def change_parent_dir(self):
        self.path = str(Path(os.path.abspath(self.path)).parent)
        self.refreshTree()

    def process_directory(self, parent, path):
        try:
            ls = []
            for p in os.listdir(path):
                abspath = os.path.join(path, p)
                isdir = os.path.isdir(abspath)

                if isdir:
                    item = '\u2514 ' + str(p)
                    ls.append(item)
                    continue

                else:
                    item = str(p)
                    ls.append(item)
            ls.sort()

            for items in ls:
                if items.startswith('\u2514'):
                    self.tree.insert(parent, 'end', text=str(items), open=False, tags='subfolder')
                else:
                    self.tree.insert(parent, 'end', text=str(items), open=False, tags='row')

        except Exception:
            return

    @staticmethod
    def ignore(_=None):
        # workaround for dismiss on_double_click_treeview to open file twice
        # step 1
        return 'break'

    def on_double_click_treeview(self, event):
        item = self.tree.identify('item', event.x, event.y)
        # print("you clicked on", self.tree.item(item,"text"))
        if self.tree.item(item, "text") == '':

            d = self.path
            d = self.checkPath(d)
            directory = tk.filedialog.askdirectory(initialdir=d)
            if not directory:
                return
            try:
                os.chdir(directory)
                for i in self.tree.get_children():
                    self.tree.delete(i)
                path = '.'
                abspath = os.path.abspath(path)
                root_node = self.tree.insert('', 'end', text=abspath, open=True, tags='folder')
                self.process_directory(root_node, abspath)

            except Exception:
                return

        elif self.tree.item(item, "text").startswith('\u2514'):
            root = self.path
            sub = self.tree.item(item, "text").split()[1]
            dir = os.path.join(root, sub)
            self.path = dir

            self.selected = None
            self.refreshTree()

        else:
            file = self.tree.item(item, "text")
            dir = self.path
            dir = self.checkPath(dir)
            filename = dir + '/' + file
            self.tree.config(cursor="X_cursor")
            self.tree.bind('<Double-1>', self.ignore)
            print(filename)
            try:
                self.opencommand(filename)
            except Exception:
                pass

            self.tree.config(cursor='')
            self.tree.update()
            self.textbox.mark_set("insert", "1.0")
            self.textbox.focus_set()

            # workaround 
            # step 2
            self.refreshTree()
            self.tree.update()
            self.tree.after(500, self.bindit)

        self.refreshTree()

    def bindit(self):
        # workaround 
        # step 3
        self.tree.bind('<Double-1>', self.on_double_click_treeview)

    @staticmethod
    def checkPath(path):
        if '\\' in path:
            path = path.replace('\\', '/')
        return path

    def on_select(self, event):
        self.selected = event.widget.selection()

    def refreshTree(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        path = self.path
        abspath = os.path.abspath(path)
        root_node = self.tree.insert('', 'end', text=abspath, open=True, tags='folder')
        self.process_directory(root_node, abspath)
