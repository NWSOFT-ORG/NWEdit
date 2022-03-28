from src.modules import tk, EditorErr


class ProgressBar(tk.Canvas):
    def __init__(self, master: tk.Toplevel):
        """A slim progressbar for the splash loading"""
        super().__init__(master, highlightthickness=0, bd=0, bg="black", height=5)
        self.master = master
        self.pack(side="bottom", fill="x")
        self.update()
        self.width = self.winfo_width()

    def set_sections(self, sections: int):
        self.sections = sections
        self.width_per_sec = self.width // sections

    def set_progress(self, number: int):
        if number > self.sections:
            raise EditorErr("Section id is too big!")
        self.create_line(0, 0, self.width_per_sec * number, 0, width=5, fill="white")
        self.update()
        self.update_idletasks()
        if number == self.sections:
            self.master.destroy()


class SplashWindow(tk.Toplevel):
    def __init__(self, master: tk.Tk):
        """The splash window, which welcomes user to use PyPlus"""
        super().__init__(master, cursor="watch")
        self.title("")
        master.withdraw()
        self.overrideredirect(False)
        self.overrideredirect(True)

        self.image = tk.PhotoImage(file="Images/splash.gif")
        self.h = h = self.image.height()
        self.w = w = self.image.width()
        self.geometry(f"{w}x{h}")
        self.place_center()

        self.canvas = tk.Canvas(self, bg="white", highlightthickness=0, bd=0)
        self.canvas.pack(fill="both", expand=True)
        self.canvas.create_image(0, 0, anchor="nw", image=self.image)

        self.progressbar = ProgressBar(self)
        self.set_section, self.set_progress = (
            self.progressbar.set_sections,
            self.progressbar.set_progress,
        )

        master.createcommand(
            "tk::mac::Quit", lambda: 0
        )  # Don't let the window close on start
        self.protocol("WM_DELETE_WINDOW", lambda: 0)  # Sort of javascript:void(0);
        self.bind("<Destroy>", lambda _: master.deiconify())

    def place_center(self):
        screen_height = self.winfo_screenheight()
        screen_width = self.winfo_screenwidth()
        offset_x = (screen_width - self.w) // 2
        offset_y = (screen_height - self.h) // 2
        self.geometry(f"+{offset_x}+{offset_y}")