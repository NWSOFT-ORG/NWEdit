#!/usr/bin/python3
from src import pyplus
from src.modules import tk

root = tk.Tk()
pyplus.Editor(master=root)  # Starts the Editor
root.mainloop()