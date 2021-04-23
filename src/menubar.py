from src.modules import ttk, tk, ScrolledFrame


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
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    def add_cascade(self, label: str, menu: MenuItem) -> None:
        frame = ScrolledFrame(self)
        for index, item in enumerate(menu.items):
            image = menu.images[index]
            command = menu.commands[index]
            btn = ttk.Button(
                frame, text=item, image=image, command=command
            )
            btn.pack(side='left', fill='both')
        self.add(text=label, child=frame)
