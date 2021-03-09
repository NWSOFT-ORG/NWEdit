from modules import *


class FileTree(ttk.Frame):
    def __init__(self, master, path, opencommand):
        ttk.Frame.__init__(self, master)
        self.selected = None
        self.opencommand = opencommand
        self.tree = ttk.Treeview(self)
        ysb = ttk.Scrollbar(self, orient='vertical', command=self.tree.yview)
        xsb = ttk.Scrollbar(self, orient='horizontal', command=self.tree.xview)
        self.tree.configure(yscroll=ysb.set, xscroll=xsb.set)
        self.tree.heading('#0', text='Directory Structure', anchor='w')

        abspath = os.path.abspath(path)
        root_node = self.tree.insert('', 'end', text=abspath, open=True)
        self.process_directory(root_node, abspath)

        ysb.pack(side="right", fill='y')
        xsb.pack(side='bottom', fill='x')
        self.tree.pack(fill='both', expand=1)
        self.tree.bind("<Double-1>", self.on_double_click_treeview)
        self.pack(side='left', fill='both', expand=1, anchor='nw')

    def process_directory(self, parent, path):
        for p in os.listdir(path):
            abspath = os.path.join(path, p)
            isdir = os.path.isdir(abspath)
            oid = self.tree.insert(parent, 'end', text=p, open=False)
            if isdir:
                self.process_directory(oid, abspath)

    def on_double_click_treeview(self, event):
        item = self.tree.identify('item', event.x, event.y)
        if '/' in self.tree.item(item, "text") or '\\' in self.tree.item(item, "text"):
            os.chdir('..')
            return 'break'
        else:
            file = self.tree.item(item, "text")
            _dir = os.getcwd()
            filename = _dir + '/' + file
            self.opencommand(file=filename)
