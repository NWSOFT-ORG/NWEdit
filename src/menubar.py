from src.modules import tk, ttk
from src.statusbar import bind_events


class MenuItem:
    def __init__(self) -> None:
        self.items = []
        self.commands = []
        self.images = []

    def add_command(
        self, label: str = None, command: callable = None, image: tk.PhotoImage = None
    ) -> None:
        self.items.append(label)
        self.commands.append(command)
        self.images.append(image)
        

class Menu(ttk.Frame):
    def __init__(self, tkwin: tk.Tk):
        super().__init__(tkwin, relief='groove')
        self.win = tkwin
    
    def add_command(self, label, command, image=None):
        if image:
            command_label = ttk.Label(self, text=label, image=image, compound="left")
        else:
            command_label = ttk.Label(self, text=label)
        
        def exec_command(_=None):
            self.place_forget()
            command()

        command_label.bind('<1>', exec_command)
        bind_events(command_label)
        command_label.pack(side='top', anchor='nw', fill='x')
    
    def tk_popup(self, x, y):
        self.place(x=x, y=y)
        if (x + self.winfo_width()) > self.win.winfo_width():
            self.place_configure(x=x, y=y, anchor='ne')

        def close_menu(_=None):
            self.place_forget()
            self.win.event_delete('<<CloseMenu>>')
        self.win.event_add('<<CloseMenu>>', '<1>')
        self.win.bind('<<CloseMenu>>', close_menu)


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
        search_button = ttk.Button(tab_frame, text='>>', width=2)
        search_button.bind('<1>', self._search_command)
        # Needs to use bind, so I can pass in x and y
        search_button.pack(side='left')
        self.commands = {}
    
    def _search_command(self, event):
        text = self.search_entry.get()
        menu = Menu(self.master)
        for item in sorted(self.commands.keys()):
            if text in item:
                menu.add_command(label=item,
                                 command=self.commands[item]
                                )
        menu.tk_popup(event.x_root, event.y_root)

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
            font="Arial 14",
        )

        label_widget.pack(side='left', fill='both', anchor='nw')

        def click(_):
            dropdown.tk_popup(
                label_widget.winfo_x(),
                label_widget.winfo_y() + label_widget.winfo_height(),
            )

        bind_events(label_widget)
        label_widget.bind("<1>", click, True)
