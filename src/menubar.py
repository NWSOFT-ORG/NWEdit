from src.modules import tk, ttk
from src.scrollableframe import ScrolledFrame


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


class Menubar(ttk.Frame):
    def __init__(
        self,
        master: tk.Tk,
    ) -> None:
        super().__init__(master)
        style = ttk.Style()
        style.layout(
            "Tab",
            [
                (
                    "Notebook.tab",
                    {
                        "sticky": "nswe",
                        "children": [
                            (
                                "Notebook.padding",
                                {
                                    "side": "top",
                                    "sticky": "nswe",
                                    "children": [
                                        (
                                            "Notebook.label",
                                            {"side": "top", "sticky": ""},
                                        )
                                    ],
                                },
                            )
                        ],
                    },
                )
            ],
        )
        self.pack(fill="x", side="top")
        self.notebook = ttk.Notebook(self)
        tab_frame = ttk.Frame(self)
        tab_frame.place(relx=1.0, x=0, y=1, anchor='ne')
        self.search_entry = ttk.Entry(tab_frame, width=15)
        self.search_entry.pack(side='left')
        search_button = ttk.Button(tab_frame, text='>>', width=2)
        search_button.bind('<1>', self._search_command)
        # Needs to use bind, so I can pass in x and y
        search_button.pack(side='left')
        self.notebook.pack(fill='both', expand=1)
        self.commands = {}
    
    def _search_command(self, event):
        text = self.search_entry.get()
        menu = tk.Menu(event.widget, tearoff=0)
        for item in sorted(self.commands.keys()):
            if text in item:
                menu.add_command(label=item,
                                 command=self.commands[item]
                                )
        menu.tk_popup(event.x_root, event.y_root)

    def add_cascade(self, label: str, menu: MenuItem) -> None:
        frame = ScrolledFrame(self)
        for index, item in enumerate(menu.items):
            command = menu.commands[index]
            image = menu.images[index]
            btn = ttk.Button(
                frame.interior, text=item, image=image, command=command, compound="top"
            )
            btn.pack(side="left", anchor="nw", fill='both')
            self.commands[item] = command
        self.notebook.add(frame, text=label, sticky="nsew")