from src.modules import tk


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

    def merge(self, menu):
        for index, item in enumerate(menu.items):
            self.items.append(item)
            self.commands.append(menu.commands[index])
            self.images.append(menu.images[index])
