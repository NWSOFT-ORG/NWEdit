"""A modded version of tkinter.Text"""

from settings import *


class TextLineNumbers(tk.Canvas):
    """Line numbers class for tkinter text widgets. From stackoverflow."""

    def __init__(self, *args, **kwargs):
        tk.Canvas.__init__(self, *args, **kwargs)
        self.textwidget = None

    def attach(self, text_widget):
        self.textwidget = text_widget

    def redraw(self, line):
        """redraw line numbers"""
        self.delete("all")

        i = self.textwidget.index("@0,0")
        w = len(self.textwidget.index("end-1c linestart"))
        self.config(width=w * 10)
        while True:
            dline = self.textwidget.dlineinfo(i)
            if dline is None:
                break
            y = dline[1]
            linenum = str(i).split(".")[0]

            if str(int(float(i))) == str(line):
                bold = font.Font(family=self.textwidget['font'], weight='bold')
                self.create_text(2,
                                 y,
                                 anchor="nw",
                                 text=linenum,
                                 fill='black',
                                 font=bold)
            else:
                self.create_text(2,
                                 y,
                                 anchor="nw",
                                 text=linenum,
                                 fill='black',
                                 font=self.textwidget['font'])
            i = self.textwidget.index("%s+1line" % i)


class EnhancedText(tk.Text):
    """Text widget, but 'records' your key actions
If you hit a key, or the text widget's content has changed,
it generats an event, to redraw the line numbers."""

    def __init__(self, *args, **kwargs):
        tk.Text.__init__(self, *args, **kwargs)

        # create a proxy for the underlying widget
        self._orig = self._w + "_orig"
        self.tk.call("rename", self._w, self._orig)
        self.tk.createcommand(self._w, self._proxy)

    def _proxy(self, *args):
        try:
            # The text widget might throw an error while pasting text!
            # let the actual widget perform the requested action
            cmd = (self._orig,) + args
            result = self.tk.call(cmd)

            # generate an event if something was added or deleted,
            # or the cursor position changed
            if (args[0] in ("insert", "replace", "delete")
                    or args[0:3] == ("mark", "set", "insert")
                    or args[0:2] == ("xview", "moveto")
                    or args[0:2] == ("xview", "scroll")
                    or args[0:2] == ("yview", "moveto")
                    or args[0:2] == ("yview", "scroll")):
                self.event_generate("<<Change>>", when="tail")

            # return what the actual widget returned

            return result
        except Exception:
            pass


class EnhancedTextFrame(ttk.Frame):
    """An enhanced text frame to put the
text widget with linenumbers in."""

    def __init__(self, *args, **kwargs):
        ttk.Frame.__init__(self, *args, **kwargs)
        settings_class = Settings()
        self.font = settings_class.get_settings('font')
        self.text = EnhancedText(self,
                                 bg='black',
                                 fg='white',
                                 insertbackground='white',
                                 selectforeground='black',
                                 selectbackground='white',
                                 highlightthickness=0,
                                 font=self.font,
                                 wrap='none',
                                 insertwidth=3)
        self.linenumbers = TextLineNumbers(self,
                                           width=30,
                                           bg='gray',
                                           bd=0,
                                           highlightthickness=0)
        self.linenumbers.attach(self.text)

        self.linenumbers.pack(side="left", fill="y")
        xscroll = ttk.Scrollbar(self,
                                command=self.text.xview,
                                orient='horizontal')
        xscroll.pack(side='bottom', fill='x', anchor='nw')
        yscroll = ttk.Scrollbar(self, command=self.text.yview)
        self.text['yscrollcommand'] = yscroll.set
        yscroll.pack(side='right', fill='y')
        self.text.pack(side="right", fill="both", expand=True)

        self.text['xscrollcommand'] = xscroll.set

        self.text.bind("<<Change>>", self._on_change)
        self.text.bind("<Configure>", self._on_change)

    def _on_change(self, _=None):
        currline = int(float(self.text.index('insert linestart')))
        self.linenumbers.redraw(currline)
        self.text.config(font=self.font)
