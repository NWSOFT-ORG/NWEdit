#!/usr/bin/python3
from src import editor
from src.modules import tk

root = tk.Tk()
editor.Editor(master=root)  # Starts the Editor
root.mainloop()