from modules import *
from settings import *


class StringDialog:
	def __init__(self, *args, **kwargs):
		self.master = tk.Toplevel(*args, **kwargs)
		self.master.title('Input')
		settings = Settings()
		ttkthemes.ThemedStyle(self.master).set_theme(settings.get_settings('theme'))
		self.content = ''
		self.label = ttk.Label(self.master, text='', justify='left')
		self.entry = tk.Entry(self.master)
		self.buttonframe = tk.Frame(self.master)
		self.label.pack()
		self.entry.pack(fill='x', anchor='nw', side='top', expand=1)
		self.buttonframe.pack()
		self.okbtn = ttk.Button(self.buttonframe, text='Ok', command=self.ok)
		self.okbtn.pack(side='left', expand=1)
		self.cancelbtn = ttk.Button(self.buttonframe, text='Cancel', command=self.cancel)
		self.cancelbtn.pack(side='right', expand=1)

	def setstring(self, string):
		self.label.config(text=string)

	def ok(self):
		if not self.entry.get():
			return
		self.content = self.entry.get()
		self.master.destroy()

	def cancel(self):
		self.master.destroy()
