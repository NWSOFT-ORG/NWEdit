import tkinter as tk
from tkinter import ttk
from typing import Callable, Literal

import json5 as json
from PIL import Image, ImageDraw, ImageFont, ImageTk

from src.Components.filedialog import FileOpenDialog
from src.Components.scrollbar import Scrollbar
from src.constants import OSX
from src.SettingsParser.project_settings import RecentProjects
from src.types import Tk_Widget

COLORS = [(255, 127, 77, 255),  # Red
          (32, 59, 53, 255),  # Dark blue
          (106, 179, 126, 255),  # Light bluish-green
          (26, 173, 139, 255),  # Cyan
          (173, 203, 84, 255),  # Yellowish-green
          (255, 207, 77, 255),  # Orange
          (105, 148, 240, 255),  # Purplish-blue
          (141, 50, 212, 255)  # Light Purple
          ]
index = 0


def create_img_with_txt(text: Literal[""]):
    global index
    with Image.new("RGBA", (250, 180)) as i:
        img = ImageDraw.Draw(i)
        img.rounded_rectangle(
            (0.0, 0.0, 175.0, 175.0),
            50,
            fill=COLORS[index % 8],
            outline=(255, 255, 255, 255)
        )
        font = ImageFont.truetype("Images/Fonts/OpenSans-CondBold.ttf", 120)
        img.text((20, 10), text, fill=(255, 255, 255, 255), font=font)

        index += 1

    i = i.resize((50, 36), 1)
    return ImageTk.PhotoImage(i)


class ProjectList(ttk.Treeview):
    def __init__(self, master: Tk_Widget, func: Callable):
        self.style = ttk.Style(master)
        self.master = master
        super().__init__(master, style="Projects.Treeview", show="tree")

        self["columns"] = ("#0", "#1", "#2")
        self.column("#0", stretch=False, width=60, anchor="nw")
        self.column("#2", stretch=True, width=300)

        self.style.configure('Projects.Treeview', rowheight=40)
        self.style.layout(
            "Projects.Treeview.Heading",
            [("Treeheading.cell", {"sticky": "nswe"}),
             ("Treeheading.border", {
                 "sticky": "nswe", "children": [
                     ("Treeheading.padding", {
                         "sticky": "nswe", "children": [
                             ("Treeheading.text", {"sticky": "nsew", "side": "left"})
                         ]
                     })
                 ]
             })
             ]
        )

        self.bind(f"<Button-{2 if OSX else 3}>", self.right_click)
        self.bind(f"<Double-1>", self.open)
        self.open_f = func

        self.settings = RecentProjects(self.master)
        self.images = []
        self.insert_projects()

    def insert_projects(self):
        y_loc = self.yview()[0]
        self.delete(*self.get_children())
        with open("EditorStatus/recent_projects.json") as f:
            config = json.load(f)
        if not isinstance(config, dict):
            return
        for key in config.keys():
            if path := config[key]["icon"]:
                self.images.append(tk.PhotoImage(file=path))
            else:
                self.images.append(create_img_with_txt(key[0:2].title()))
            path = self.settings.get_path_to(key)
            self.insert("", "end", values=(key, path), image=self.images[-1])

        self.yview_moveto(y_loc)

    def right_click_menu(self, event: tk.Event) -> tk.Menu:
        menu = tk.Menu(self.master)
        item = self.identify("item", event.x, event.y)
        name = self.item(item, "values")[0]
        menu.add_command(label="Open Project", command=lambda: self.open(event))
        menu.add_command(label="Remove from Projects", command=lambda: self.remove_project(name))
        menu.add_command(label="Assign Icon...", command=lambda: self.assign_icon(name))
        menu.add_separator()
        menu.add_command(label="Refresh...", command=self.insert_projects)

        return menu

    def remove_project(self, name):
        self.settings.remove_project(name)
        self.insert_projects()

    def assign_icon(self, name):
        FileOpenDialog(self.master, lambda file: self.settings.assign_icon(name, icon=file), action="Select")
        self.insert_projects()

    def right_click(self, event: tk.Event):
        item = self.identify("item", event.x, event.y)
        self.selection_set(item)
        self.right_click_menu(event).post(event.x_root, event.y_root)

    def open(self, event):
        item = self.identify("item", event.x, event.y)
        if not item:
            return
        text = self.item(item, "values")[0]

        self.open_f(text)


class ProjectView(ttk.Frame):
    def __init__(self, master, open_func):
        super().__init__(master)
        self.project_list = ProjectList(self, open_func)
        self.project_list.pack(side="left", fill="both", expand=True)

        scrollbar = Scrollbar(self, self.project_list.yview)
        scrollbar.pack(side="right", fill="y")
        self.project_list["yscrollcommand"] = scrollbar.set


def _open_func(file):
    print(file)


if __name__ == "__main__":
    root = tk.Tk()
    pv = ProjectView(root, _open_func)
    pv.pack(fill="both", expand=True)
    root.mainloop()
