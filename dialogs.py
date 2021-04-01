from treeview import *


class Dialog(tk.Toplevel):
    def __init__(self, parent: tk.Misc, title: str = None):

        super().__init__(parent)
        self.transient(parent)

        if title:
            self.title(title)

        self.parent = parent

        self.result = None

        body = ttk.Frame(self)
        self.initial_focus = self.body(body)
        body.pack(padx=5, pady=5)

        self.buttonbox()

        if not self.initial_focus:
            self.initial_focus = self

        self.protocol("WM_DELETE_WINDOW", self.cancel)

        self.initial_focus.focus_set()
        self.resizable(0, 0)
        self.wait_window(self)

    def body(self, master: tk.Misc):
        # create dialog body.  return widget that should have
        # initial focus.  this method should be overridden

        pass

    def buttonbox(self):
        # add standard button box. override if you don't want the
        # standard buttons

        box = ttk.Frame(self)
        # box.configure(bg='black')

        w = ttk.Button(box,
                       text="OK",
                       width=10,
                       command=self.ok,
                       default=tk.ACTIVE)
        w.pack(side='left', padx=5, pady=5)
        w = ttk.Button(box, text="Cancel", width=10, command=self.cancel)
        w.pack(side='left', padx=5, pady=5)

        # self.bind("<Return>", self.ok)
        # self.bind("<Escape>", self.cancel)

        box.pack()

    def ok(self, _=None):
        if not self.validate():
            self.initial_focus.focus_set()  # put focus back
            return

        self.withdraw()
        self.update_idletasks()

        self.apply()

        self.cancel()

    def cancel(self, _=None):

        # put focus back to the parent window
        self.parent.focus_set()
        self.destroy()

    @staticmethod
    def validate():
        return 1  # override

    @staticmethod
    def apply():
        pass  # override


class MessageYesNoDialog(Dialog):
    def __init__(self, parent: tk.Misc, title: str, text: str = None):
        self.text = text
        super().__init__(parent, title)

    def body(self, master):
        label1 = ttk.Label(master, text=self.text)
        label1.pack()

        return label1

    def buttonbox(self):
        box = ttk.Frame(self)

        b1 = ttk.Button(box, text="Yes", width=10, command=self.apply)
        b1.pack(side='left', padx=5, pady=5)
        b2 = ttk.Button(box, text="No", width=10, command=self.cancel)
        b2.pack(side='left', padx=5, pady=5)

        box.pack()

    def apply(self, _=None):
        self.result = 1
        self.parent.focus_set()
        self.destroy()

    def cancel(self, _=None):
        # put focus back to the parent window
        self.result = 0
        self.parent.focus_set()
        self.destroy()


class InputStringDialog(Dialog):
    def __init__(self, parent, title='InputString', text=None):
        self.text = text
        super().__init__(parent, title)

    def body(self, master: tk.Misc):
        label1 = ttk.Label(master, text=self.text)
        label1.pack(side='top', fill='both', expand=1)

        return label1

    def buttonbox(self):
        self.entry = ttk.Entry(self)
        self.entry.pack(fill='x', expand=1)
        box = ttk.Frame(self)

        b1 = ttk.Button(box, text="Ok", width=10, command=self.apply)
        b1.pack(side='left', padx=5, pady=5)
        b2 = ttk.Button(box, text="Cancel", width=10, command=self.cancel)
        b2.pack(side='left', padx=5, pady=5)

        box.pack()

    def apply(self, _=None):
        self.result = self.entry.get()
        self.parent.focus_set()
        self.destroy()

    def cancel(self, _=None):
        # put focus back to the parent window
        self.result = 0
        self.parent.focus_set()
        self.destroy()


class ErrorDialog(Dialog):
    def __init__(self, parent: tk.Misc, text: str = None):
        self.text = text
        super().__init__(parent, 'Error')

    def body(self, master):
        label1 = ttk.Label(master, text=self.text)
        label1.pack(side='top', fill='both', expand=1)

        return label1

    def buttonbox(self):
        b1 = ttk.Button(self, text="Ok", width=10, command=self.apply)
        b1.pack(side='left', padx=5, pady=5)

    def apply(self, _=None):
        self.parent.focus_set()
        self.destroy()

    @staticmethod
    def cancel(_=None, **kwargs):
        pass


class FileOpenDialog(FileTree):
    def __init__(self, opencommand: callable):
        self.win = tk.Toplevel()
        self.win.title('Open a file')
        self.win.resizable(0, 0)
        self.buttonframe = ttk.Frame(self.win)
        self.okbtn = ttk.Button(self.buttonframe,
                                text='Open',
                                command=self.on_double_click_treeview)
        self.okbtn.pack(side='left')
        self.cancelbtn = ttk.Button(self.buttonframe,
                                    text='Cancel',
                                    command=self.win.destroy)
        self.cancelbtn.pack(side='right')
        self.buttonframe.pack(side='bottom', anchor='nw')
        self.entryframe = ttk.Frame(self.win)
        self.pathentry = ttk.Entry(self.entryframe)
        self.pathentry.pack(fill='x')
        self.open_from_string_btn = ttk.Button(self.pathentry,
                                               command=self.open_from_string,
                                               text='>> Open')
        self.open_from_string_btn.pack(side='right')
        self.entryframe.pack(fill='x')
        super().__init__(master=self.win,
                         opencommand=opencommand,
                         path=os.path.expanduser('~'),
                         showbuttonframe=False)

    def open_from_string(self, _=None):
        try:
            file = self.pathentry.get()
            if os.path.isfile(file):
                self.saveascommand(file)
                return
            path = self.path
            file = os.path.join(path, self.pathentry.get())
            if os.path.isdir(file):
                self.path = file
                self.refresh_tree()
            else:
                self.saveascommand(file)
        except Exception:
            pass

    def on_double_click_treeview(self, _=None):
        try:
            item = self.tree.focus()
            tag = self.tree.item(item, "tags")[0]
            if tag == 'subfolder':
                root = self.path
                sub = self.tree.item(item, "text")
                _dir = os.path.join(root, sub)
                self.path = _dir
                self.refresh_tree()
                return

            elif tag == 'folder':
                self.refresh_tree()
                return

            else:
                file = self.tree.item(item, "text")
                _filename = os.path.join(self.path, file)
                try:
                    self.win.destroy()
                    self.saveascommand(_filename)
                except Exception:
                    pass

                self.tree.update()
                self.refresh_tree()

            self.refresh_tree()
        except Exception:
            pass


class FileSaveAsDialog(FileTree):
    def __init__(self, savecommand: callable):
        self.win = tk.Toplevel()
        self.win.title('Save As...')
        self.win.resizable(0, 0)
        self.buttonframe = ttk.Frame(self.win)
        self.okbtn = ttk.Button(self.buttonframe,
                                text='Save',
                                command=self.on_double_click_treeview)
        self.okbtn.pack(side='left')
        self.cancelbtn = ttk.Button(self.buttonframe,
                                    text='Cancel',
                                    command=self.win.destroy)
        self.cancelbtn.pack(side='right')
        self.buttonframe.pack(side='bottom', anchor='nw')
        self.entryframe = ttk.Frame(self.win)
        self.pathentry = ttk.Entry(self.entryframe)
        self.pathentry.pack(fill='x')
        self.open_from_string_btn = ttk.Button(self.pathentry,
                                               command=self.saveas_from_string,
                                               text='>> Save')
        self.open_from_string_btn.pack(side='right')
        self.entryframe.pack(fill='x')

        def save(_=None):
            savecommand()
            self.init_ui()

        super().__init__(master=self.win,
                         opencommand=save,
                         path=os.path.expanduser('~'),
                         showbuttonframe=False)

    def saveas_from_string(self, _=None):
        try:
            file = self.pathentry.get()
            if os.path.isfile(file):
                self.saveascommand(file)
                return
            path = self.path
            file = os.path.join(path, self.pathentry.get())
            if os.path.isdir(file):
                self.path = file
                self.refresh_tree()
            else:
                self.saveascommand(file)
        except Exception:
            pass

    def on_double_click_treeview(self, _=None):
        try:
            item = self.tree.focus()
            tag = self.tree.item(item, "tags")[0]
            if tag == 'subfolder':
                root = self.path
                sub = self.tree.item(item, "text")
                _dir = os.path.join(root, sub)
                self.path = _dir
                self.refresh_tree()
                return

            elif tag == 'folder':
                self.refresh_tree()
                return

            else:
                file = self.tree.item(item, "text")
                _filename = os.path.join(self.path, file)
                try:
                    self.win.destroy()
                    self.saveascommand(_filename)
                except Exception:
                    pass

                self.tree.update()
                self.refresh_tree()

            self.refresh_tree()
        except Exception:
            pass
