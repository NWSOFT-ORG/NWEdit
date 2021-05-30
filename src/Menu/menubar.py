from src.modules import tk, ttk
from src.statusbar import bind_events
from src.Menu.yscrolledframe import ScrollableFrame


class MenuItem:
	def __init__(self) -> None:
		self.items = []
		self.commands = []
		self.images = []

	def add_command(self,
	                label: str = None,
	                command: callable = None,
	                image: tk.PhotoImage = None) -> None:
		self.items.append(label)
		self.commands.append(command)
		self.images.append(image)


class Menu(ScrollableFrame):
	def __init__(self, tkwin: tk.Tk):
		super().__init__(tkwin, relief='groove')
		self.win = tkwin
		self.opened = False

	def add_command(self, label, command, image=None):
		if image:
			command_label = ttk.Label(self.frame,
			                          text=label,
			                          image=image,
			                          compound="left")
		else:
			command_label = ttk.Label(self.frame, text=label)

		def exec_command(_=None):
			self.place_forget()
			self.opened = False
			command()

		command_label.bind('<1>', exec_command)
		bind_events(command_label)
		command_label.pack(side='top', anchor='nw', fill='x')

	def tk_popup(self, x, y):
		self.place(x=x, y=y)
		if (x + self.winfo_width()) > self.win.winfo_width():
			self.place_configure(x=(x - self.winfo_width()), y=y, anchor='ne')
		self.opened = True

		def close_menu(event=None):
			if not (event.x_root in range(self.winfo_x(),
		            self.winfo_x() + self.winfo_width() + 1)
			    and event.y_root in range(self.winfo_y(),
			                     self.winfo_y() + self.winfo_height() + 1)):
				self.place_forget()
				self.win.event_delete('<<CloseMenu>>')
				self.opened = False

		self.win.event_add('<<CloseMenu>>', '<1>')
		self.win.bind('<<CloseMenu>>', close_menu)

	def unpost(self):
		self.opened = False
		self.place_forget()


class Menubar(ttk.Frame):
	def __init__(
	    self,
	    master: tk.Tk,
	) -> None:
		super().__init__(master)
		self.pack(fill="x", side="top")
		tab_frame = ttk.Frame(self)
		tab_frame.place(relx=1.0, x=0, y=1, anchor='ne')
		self.search_entry = ttk.Entry(tab_frame, width=15)
		self.search_entry.pack(side='left', fill='both')
		self.search_button = ttk.Button(tab_frame,
		                                text='>>',
		                                width=3,
		                                command=self._search_command)
		self.search_button.pack(side='left')
		self.commands = {}
		self.menus = []
		self.menu_opened = None

	def _search_command(self):
		text = self.search_entry.get()
		menu = Menu(self.master)
		for item in sorted(self.commands.keys()):
			if text in item:
				menu.add_command(label=item, command=self.commands[item])
		menu.tk_popup(
		    self.winfo_x() + self.winfo_width() +
		    self.search_button.winfo_x() + self.search_button.winfo_width(),
		    self.search_button.winfo_y() + self.search_button.winfo_height())

	def add_cascade(self, label: str, menu: MenuItem) -> None:
		dropdown = Menu(self.master)
		for index, item in enumerate(menu.items):
			command = menu.commands[index]
			dropdown.add_command(item, command, menu.images[index])
			self.commands[item] = command

		label_widget = ttk.Label(
		    self,
		    text=label,
		    padding=[1, 3, 6, 1],
		    font="Arial 12",
		)

		label_widget.pack(side='left', fill='both', anchor='nw')

		def click(_):
			self.menu_opened = dropdown
			dropdown.tk_popup(
			    label_widget.winfo_x(),
			    label_widget.winfo_y() + label_widget.winfo_height(),
			)

		def enter(event):
			if self.menu_opened:
				if self.menu_opened.opened:
					self.menu_opened.unpost()
					click(event)
			label_widget.state(('active', ))

		def leave(_):
			label_widget.state(('!active', ))

		label_widget.bind('<Leave>', leave)
		label_widget.bind('<Enter>', enter)
		label_widget.bind("<1>", click, True)
