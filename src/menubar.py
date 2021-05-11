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
        closeaction: callable,
        minimiseaction: callable,
        maximiseaction: callable,
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
        master.overrideredirect(0)
        master.overrideredirect(1)

        x, y = 0, 0
        def mouse_motion(event):
            global x, y
            # Positive offset represent the mouse is moving to the lower right corner, negative moving to the upper left corner
            offset_x, offset_y = event.x - x, event.y - y  
            new_x = master.winfo_x() + offset_x
            new_y = master.winfo_y() + offset_y
            new_geometry = f"+{new_x}+{new_y}"
            master.geometry(new_geometry)

        def mouse_press(event):
            global x, y
            x, y = event.x, event.y

        self.notebook.bind("<B1-Motion>", mouse_motion)  # Hold the left mouse button and drag events
        self.notebook.bind("<Button-1>", mouse_press)  # The left mouse button press event, long calculate by only once

        button_frame = ttk.Frame(self)
        closeicon = tk.PhotoImage(file="Images/close.gif")
        maximiseicon = tk.PhotoImage(file="Images/maximise.gif")
        minimiseicon = tk.PhotoImage(file="Images/minimise.gif")
        close = ttk.Label(button_frame, image=closeicon)
        close.image = closeicon
        close.bind('<1>', closeaction)
        close.pack(side="right")
        maximise = ttk.Label(button_frame, image=maximiseicon)
        maximise.image = maximiseicon
        maximise.bind('<1>', maximiseaction)
        maximise.pack(side="right")
        minimise = ttk.Label(button_frame, image=minimiseicon)
        minimise.image = minimiseicon
        minimise.bind('<1>', minimiseaction)
        minimise.pack(side="right")
        button_frame.place(relx=1.0, x=0, y=1, anchor="ne")
        self.notebook.pack(fill="both", expand=True)

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
