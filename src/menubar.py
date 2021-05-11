from src.modules import ScrolledFrame, tk, ttk


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
        self.notebook.pack(fill='both', expand=1)

    def add_cascade(self, label: str, menu: MenuItem) -> None:
        frame = ScrolledFrame(self)
        for index, item in enumerate(menu.items):
            command = menu.commands[index]
            image = menu.images[index]
            btn = ttk.Button(
                frame.interior, text=item, image=image, command=command, compound="top"
            )
            btn.pack(side="left", anchor="nw")
        self.notebook.add(frame, text=label, sticky="nsew")
