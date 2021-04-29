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


class Menubar(ttk.Notebook):
    def __init__(self, master) -> None:
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
        super().__init__(master)

    def add_cascade(self, label: str, menu: MenuItem) -> None:
        frame = ScrolledFrame(self)
        for index, item in enumerate(menu.items):
            image = menu.images[index]
            command = menu.commands[index]
            btn = ttk.Button(
                frame.interior, text=item, image=image, command=command, compound="top"
            )
            btn.pack(side="left", anchor="nw")
        self.add(frame, text=label)
