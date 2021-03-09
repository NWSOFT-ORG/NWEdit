"""Closable ttk.Notebook"""


class ClosableNotebook(ttk.Notebook):
    """A ttk Notebook with close buttons on each tab
images drawn by me using the mspaint app (the rubbish in many people's opinion)

Change the layout, makes it look like this:
+------------+
| title   [X]|
+-------------------------"""

    __initialized = False

    def __init__(self, master, cmd):
        if not self.__initialized:
            self.__initialize_custom_style()
            self.__inititialized = True
        ttk.Notebook.__init__(self, master=master, style='CustomNotebook')
        self.cmd = cmd

        self._active = None

        self.bind("<ButtonPress-1>", self.on_close_press, True)
        self.bind("<ButtonRelease-1>", self.on_close_release)

    def on_close_press(self, event):
        """Called when the button is pressed over the close button"""

        element = self.identify(event.x, event.y)

        if "close" in element:
            index = self.index("@%d,%d" % (event.x, event.y))
            self.state(['pressed'])
            self._active = index
        else:
            self.event_generate("<<Notebook_B1-Down>>", when="tail")

    def on_close_release(self, event):
        try:
            """Called when the button is released over the close button"""
            if not self.instate(['pressed']):
                return

            element = self.identify(event.x, event.y)
            index = self.index("@%d,%d" % (event.x, event.y))

            if "close" in element and self._active == index:
                self.cmd()

            self.state(["!pressed"])
            self._active = None
        except Exception:
            pass

    def __initialize_custom_style(self):
        style = ttk.Style()
        self.images = (tk.PhotoImage("img_close",
                                     data='''iVBORw0KGgoAAAANSUhEUgAAACAAAAAgA
            gMAAAAOFJJnAAAAAXNSR0IB2cksfwAAAAlwSFlzAAALEwAACxMBAJqcGAAAAAxQTFRFA
            AAAAAAA/yYA////nxJg7AAAAAR0Uk5TAP///7MtQIgAAACMSURBVHicPZC9AQMhCIVJk
            yEyTZbIEnfLZIhrTgtHYB9HoIB7/CiFfArCA6JfGNGrhX3pnfCnT3i+6BQHu+lU+O5gg
            KE3HTaRIgBGkk3AUKQ0AE4wAO+IOrDwDBiKCg7dNKGZFPCCFepWyfg1Vx2pytkCvbIpr
            inDq4QwV5hSS/yhNc4ecI+8l7DW8gDYFaqpCCFJsQAAAABJRU5ErkJggg==
                '''),
                       tk.PhotoImage("img_closeactive",
                                     data='''iVBORw0KGgoAAAANSUhEUgAAACA
            AAAAgBAMAAACBVGfHAAAAAXNSR0IB2cksfwAAAAlwSFlzAAALEwAACxMBAJqcGAAAAA9
            QTFRFAAAAAAAA/YAI////////uHhEXgAAAAV0Uk5TAP///zOOAqjJAAAAk0lEQVR4nGW
            S2RGAMAhE44wFaDow6SD035scCwMJHxofyxGwtfYma2zXSPYw6Bl8VTCJJZ2fbkQsYbB
            CAEAhWAL07QIFLlGHAEiMK7CjYQV6RqAB+UB1AyJBZgCWoDYAS2gUMHewh0iOklSrpLL
            WR2pMval1c6bLITyu7z3EgLyFNMI65BFTtzUcizpWeS77rr/DDzkRRQdj40f8AAAAAEl
            FTkSuQmCC
                '''),
                       tk.PhotoImage("img_closepressed",
                                     data='''iVBORw0KGgoAAAANSUhEUgAAAC
            AAAAAgAgMAAAAOFJJnAAAAAXNSR0IB2cksfwAAAAlwSFlzAAALEwAACxMBAJqcGAAAAA
            xQTFRFAAAAAAAA//8K////dEqdoAAAAAR0Uk5TAP///7MtQIgAAACMSURBVHicPZC9AQ
            MhCIVJkyEyTZbIEnfLZIhrTgtHYB9HoIB7/CiFfArCA6JfGNGrhX3pnfCnT3i+6BQHu+
            lU+O5ggKE3HTaRIgBGkk3AUKQ0AE4wAO+IOrDwDBiKCg7dNKGZFPCCFepWyfg1Vx2pyt
            kCvbIprinDq4QwV5hSS/yhNc4ecI+8l7DW8gDYFaqpCCFJsQAAAABJRU5ErkJggg==
            '''))  # The images, 32x32-sized

        style.element_create(
            "close",
            "image",
            "img_close",
            ("active", "pressed", "!disabled", "img_closepressed"),
            ("active", "!disabled", "img_closeactive"),
            border=8,
            sticky='')
        style.layout("CustomNotebook", [("CustomNotebook.client", {
            "sticky": "nswe"
        })])
        style.layout("CustomNotebook.Tab", [("CustomNotebook.tab", {
            "sticky":
                "nswe",
            "children": [("CustomNotebook.padding", {
                "side":
                    "top",
                "sticky":
                    "nswe",
                "children": [("CustomNotebook.focus", {
                    "side":
                        "top",
                    "sticky":
                        "nswe",
                    "children": [
                        ("CustomNotebook.label", {
                            "side": "left",
                            "sticky": ''
                        }),
                        ("CustomNotebook.close", {
                            "side": "left",
                            "sticky": ''
                        }),
                    ]
                })]
            })]
        })])
