"""Closable ttk.Notebook"""
from src.constants import logger
from src.functions import is_dark_color, lighten_color
from src.modules import tk, ttk, ttkthemes
from src.settings import Settings
from src.statusbar import bind_events


class ClosableNotebook(ttk.Notebook):
    """A ttk Notebook with close buttons on each tab
    images drawn by me using the mspaint app (the rubbish in many people's opinion)

    Change the layout, makes it look like this:
    +------------+
    | title   [X]|
    +-------------------------"""

    __initialized = False

    def __init__(self, master, cmd):
        self.style = ttkthemes.ThemedStyle()
        self.settings = Settings()
        self.style.set_theme(self.settings.get_settings("theme"))
        self.bg = self.style.lookup("TLabel", "background")
        self.fg = self.style.lookup("TLabel", "foreground")
        if is_dark_color(self.bg):
            self.close_icon = tk.PhotoImage("img_close", file="Images/close.gif")
            self.alltabs_icon = tk.PhotoImage(file="Images/all-tabs-light.gif")
            self.nexttab_icon = tk.PhotoImage(file="Images/next-tab-light.gif")
            self.prevtab_icon = tk.PhotoImage(file="Images/prev-tab-light.gif")
        else:
            self.close_icon = tk.PhotoImage("img_close", file="Images/close-dark.gif")
            self.alltabs_icon = tk.PhotoImage(file="Images/all-tabs.gif")
            self.nexttab_icon = tk.PhotoImage(file="Images/next-tab.gif")
            self.prevtab_icon = tk.PhotoImage(file="Images/prev-tab.gif")
        if not self.__initialized:
            self.__initialize_custom_style()
            self.__inititialized = True
        super().__init__(master=master, style="CustomNotebook")
        self.cmd = cmd

        self._active = None

        self.bind("<ButtonPress-1>", self.on_close_press, True)
        self.bind("<ButtonRelease-1>", self.on_close_release)
        self.bind("<B1-Motion>", self)

        tab_frame = ttk.Frame(self)
        tab_frame.place(relx=1.0, x=0, y=1, anchor='ne')
        self.pack(expand=1, fill="both")

        def show_tab_menu(event):
            tab_menu = tk.Menu(master)
            for tab in self.tabs():
                tab_menu.add_command(label=self.tab(tab, option="text"),
                                     command=lambda temp=tab: self.select(temp))
            tab_menu.tk_popup(event.x_root, event.y_root)
        
        def prevtab(_=None):
            try:
                self.select(self.index('current') - 1)
            except tk.TclError:
                pass
        
        def nexttab(_=None):
            try:
                self.select(self.index('current') + 1)
            except tk.TclError:
                pass

        ttk.Separator(tab_frame, orient='vertical').pack(
            side='left', fill='y')

        prev_tab_label = ttk.Label(tab_frame, image=self.prevtab_icon)
        prev_tab_label.image = self.prevtab_icon
        prev_tab_label.bind("<1>", prevtab)
        prev_tab_label.pack(side='left')

        next_tab_label = ttk.Label(tab_frame, image=self.nexttab_icon)
        next_tab_label.image = self.nexttab_icon
        next_tab_label.bind("<1>", nexttab)
        next_tab_label.pack(side='left')

        ttk.Separator(tab_frame, orient='vertical').pack(side='left', fill='y')

        allitems_label = ttk.Label(tab_frame, image=self.alltabs_icon)
        allitems_label.image = self.alltabs_icon
        allitems_label.bind("<1>", show_tab_menu)
        allitems_label.pack(side='left')
        
        bind_events(prev_tab_label)
        bind_events(next_tab_label)
        bind_events(allitems_label)

    def on_close_press(self, event):
        """Called when the button is pressed over the close button"""

        element = self.identify(event.x, event.y) 
        if "close" in element:
            index = self.index("@%d,%d" % (event.x, event.y))
            self.state(["pressed"])
            self._active = index
        else:
            self.event_generate("<<Notebook_B1-Down>>", when="tail")
        logger.debug("Close tab start")

    def on_close_release(self, event):
        """Called when the button is released over the close button"""
        try:
            if not self.instate(["pressed"]):
                return

            element = self.identify(event.x, event.y)
            index = self.index("@%d,%d" % (event.x, event.y))

            if "close" in element and self._active == index:
                self.cmd()

            self.state(["!pressed"])
            self._active = None
            logger.debug("Close tab end")

        except Exception:
            logger.exception("Error:")

    def __initialize_custom_style(self):
        style = ttk.Style()
        
        try:
            style.element_create("close", "image", "img_close", border=10, sticky="")
        except tk.TclError:
            pass
        style.configure(
            "CustomNotebook.Tab", background=lighten_color(self.bg, 20, 20, 20)
        )
        style.layout(
            "CustomNotebook",
            [
                (
                    "CustomNotebook.client",
                    {
                        "sticky": "nswe",
                    },
                )
            ],
        )
        style.layout(
            "CustomNotebook.Tab",
            [
                (
                    "CustomNotebook.tab",
                    {
                        "sticky": "nswe",
                        "children": [
                            (
                                "CustomNotebook.padding",
                                {
                                    "side": "top",
                                    "sticky": "nswe",
                                    "children": [
                                        (
                                            "CustomNotebook.label",
                                            {"side": "left", "sticky": ""},
                                        ),
                                        (
                                            "CustomNotebook.close",
                                            {"side": "left", "sticky": ""},
                                        ),
                                    ],
                                },
                            )
                        ],
                    },
                )
            ],
        )
        logger.debug("Initialized custom style.")

    def move_tab(self, event: tk.EventType) -> None:
        if self.index("end") > 1:
            y = self.get_tab().winfo_y() - 5

            try:
                self.insert(
                    event.widget.index("@%d,%d" % (event.x, y)), self.select()
                )
            except tk.TclError:
                return

    def get_tab(self):
        return self.nametowidget(self.select())
