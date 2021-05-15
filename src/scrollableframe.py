from src.modules import tk, ttk, ttkthemes
from src.dialogs import get_theme


class ScrolledFrame(ttk.Frame):
    """A pure Tkinter scrollable frame that actually works!
    * Use the 'interior' attribute to place widgets inside the scrollable frame
    * Construct and pack/place/grid normally
    * This frame only allows vertical scrolling

    """

    def __init__(self, parent, *args, **kw):
        super().__init__(parent, *args, **kw)

        # create a canvas object and a vertical scrollbar for scrolling it
        scrollbar = ttk.Scrollbar(self, orient="horizontal")
        scrollbar.pack(fill="x", side="bottom")
        canvas = tk.Canvas(
            self, bd=0, highlightthickness=0, xscrollcommand=scrollbar.set, height=50
        )
        canvas.pack(fill='both', expand=1)
        self._style = ttkthemes.ThemedStyle()
        self._style.set_theme(get_theme())
        bg = self._style.lookup("TLabel", "background")
        scrollbar.config(command=canvas.xview)
        canvas.config(bg=bg)

        # create a frame inside the canvas which will be scrolled with it
        self.interior = interior = ttk.Frame(canvas, height=50)
        canvas.create_window(0, 0, window=interior, anchor="nw")

        def _configure_interior(_):
            # update the scrollbars to match the size of the inner fram
            size = (interior.winfo_reqwidth(), interior.winfo_reqheight())
            canvas.config(scrollregion="0 0 %s %s" % size)
            if interior.winfo_reqwidth() != canvas.winfo_width():
                # update the canvas's width to fit the inner fram
                canvas.config(width=interior.winfo_reqwidth())

        interior.bind("<Configure>", _configure_interior)
