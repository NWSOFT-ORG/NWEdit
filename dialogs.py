from treeview import *


class Dialog(tk.Toplevel):
	def __init__(self, parent: tk.Tk, title=None):

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

	def body(self, master):
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
	def __init__(self, parent, title, text=None):
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

	def apply(self, event=None):
		self.result = 1
		self.parent.focus_set()
		self.destroy()

	def cancel(self, event=None):
		# put focus back to the parent window
		self.result = 0
		self.parent.focus_set()
		self.destroy()


class InputStringDialog(Dialog):
	def __init__(self, parent, title='InputString', text=None):
		self.text = text
		super().__init__(parent, title)

	def body(self, master):
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

	def apply(self, event=None):
		self.result = self.entry.get()
		self.parent.focus_set()
		self.destroy()

	def cancel(self, event=None):
		# put focus back to the parent window
		self.result = 0
		self.parent.focus_set()
		self.destroy()


class ErrorDialog(Dialog):
	def __init__(self, parent, text=None):
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
	def cancel(_=None):
		pass


class FileOpenDialog(FileTree):
	def __init__(self, opencommand: callable):
		self.master = tk.Toplevel()
		self.master.title('Open a file')
		self.master.resizable(0, 0)
		icon = tk.PhotoImage(file='Images/open-16px.gif')
		self.master.iconphoto(False, icon)
		super().__init__(master=self.master,
		                 opencommand=opencommand,
		                 path=os.path.expanduser('~'))

	def on_double_click_treeview(self, event: tk.EventType):
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
				_filename = os.path.join(_dir, file)
				try:
					self.opencommand(_filename)
					self.master.destroy()
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
