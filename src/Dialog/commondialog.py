from src.constants import APPDIR, VERSION, logger
from src.modules import json, tk, ttk, ttkthemes, os, webbrowser, requests


def download_file(url, localfile='') -> str:
    """Downloads a file from remote path"""
    local_filename = url.split("/")[-1] if not localfile else localfile
    # NOTE the stream=True parameter below
    with requests.get(url, stream=True, allow_redirects=True) as r:
        r.raise_for_status()
        with open(local_filename, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                # If you have chunk encoded response uncomment if
                # and set chunk_size parameter to None.
                # if chunk:
                f.write(chunk)
    return local_filename

# Need these because importing settings is a circular import
def get_theme():
    with open(APPDIR + "/Settings/general-settings.json") as f:
        settings = json.load(f)
    return settings["theme"]


def get_font():
    with open(APPDIR + "/Settings/general-settings.json") as f:
        settings = json.load(f)
    return settings["font"]


class YesNoDialog(tk.Toplevel):
    def __init__(self, parent: tk.Misc = None, title: str = "", text: str = None):
        self.text = text
        super().__init__(parent)
        self.title(title)
        label1 = ttk.Label(self, text=self.text)
        label1.pack(fill="both")

        box = ttk.Frame(self)

        b1 = ttk.Button(box, text="Yes", command=self.apply)
        b1.pack(side="left")
        b2 = ttk.Button(box, text="No", command=self.cancel)
        b2.pack(side="left")

        box.pack(fill="x")
        self.protocol("WM_DELETE_WINDOW", self.cancel)
        self.resizable(0, 0)
        self.wait_window(self)

    def apply(self, _=None):
        self.result = 1
        self.destroy()
        logger.info("apply")

    def cancel(self, _=None):
        """put focus back to the parent window"""
        self.result = 0
        self.destroy()
        logger.info("cancel")


class InputStringDialog(tk.Toplevel):
    def __init__(self, parent='.', title='', text=''):
        super().__init__(parent)
        self.title(title)
        ttk.Label(self, text=text).pack(fill='x')
        self.entry = ttk.Entry(self)
        self.entry.pack(fill="x", expand=1)
        box = ttk.Frame(self)

        b1 = ttk.Button(box, text="Ok", command=self.apply)
        b1.pack(side="left")
        b2 = ttk.Button(box, text="Cancel", command=self.cancel)
        b2.pack(side="left")

        box.pack(fill="x")
        self.protocol("WM_DELETE_WINDOW", self.cancel)
        self.resizable(0, 0)
        self.wait_window(self)

    def apply(self):
        self.result = self.entry.get()
        self.destroy()
        logger.info("apply")

    def cancel(self):
        self.result = None
        self.destroy()
        logger.info("cancel")


class ErrorInfoDialog(tk.Toplevel):
    def __init__(self, parent: tk.Misc = None, text: str = None, title: str = "Error"):
        self.text = text
        super().__init__(parent)
        self.title(title)
        label1 = ttk.Label(self, text=self.text)
        label1.pack(side="top", fill="both", expand=1)
        b1 = ttk.Button(self, text="Ok", width=10, command=self.apply)
        b1.pack(side="left")
        self.protocol("WM_DELETE_WINDOW", self.cancel)
        self.resizable(0, 0)
        self.wait_window(self)

    def apply(self, _=None):
        self.destroy()
        logger.info("apply")

    @staticmethod
    def cancel(_=None):
        pass


class AboutDialog:
    def __init__(self, master):
        """Shows the version and related info of the editor."""
        self.master = master
        self.icon = tk.PhotoImage(file="Images/pyplus.gif")

        ver = tk.Toplevel(self.master)
        ver.transient(self.master)
        ver.resizable(0, 0)
        ver.title("About PyPlus")
        ttk.Label(ver, image=self.icon).pack(fill="both")
        ttk.Label(ver, text=f"Version {VERSION}", font="Arial 30 bold").pack(
            fill="both"
        )
        if self.check_updates(popup=False)[0]:
            update = ttk.Label(
                ver, text="Updates available", foreground="blue", cursor="hand2"
            )
            update.pack(fill="both")
            update.bind(
                "<Button-1>",
                lambda e: webbrowser.open_new_tab(self.check_updates(popup=False)[1]),
            )
        else:
            ttk.Label(ver, text="No updates available").pack(fill="both")
        ver.mainloop()

    def check_updates(self, popup=True) -> list:
        if "DEV" in VERSION:
            ErrorInfoDialog(
                text="Updates aren't supported by develop builds,\n\
            since you're always on the latest version!",
            )  # If you're on the developer build, you don't need updates!
            return [True, 'about://blank']
        download_file(
            url="https://raw.githubusercontent.com/ZCG-coder/NWSOFT/master/PyPlusWeb/ver.json"
        )
        with open("ver.json") as f:
            newest = json.load(f)
        version = newest["version"]
        if not popup:
            os.remove("ver.json")
            return [version != VERSION, newest["url"]]
        updatewin = tk.Toplevel()
        updatewin.title("Updates")
        updatewin.resizable(0, 0)
        updatewin.transient(".")
        ttkthemes.ThemedStyle(updatewin)
        if version != VERSION:
            ttk.Label(updatewin, text="Update available!", font="Arial 30").pack(
                fill="both"
            )
            ttk.Label(updatewin, text=version).pack(fill="both")
            ttk.Label(updatewin, text=newest["details"]).pack(fill="both")
            url = newest["url"]
            ttk.Button(
                updatewin, text="Get this update", command=lambda: webbrowser.open(url)
            ).pack()
        else:
            ttk.Label(updatewin, text="No updates available", font="Arial 30").pack(
                fill="both"
            )
        os.remove("ver.json")
        updatewin.mainloop()
