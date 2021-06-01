#!/usr/bin/python3
from src import editor
from src.modules import tk

if __name__ == "__main__":
    root = tk.Tk()
    editor.Editor(master=root)  # Starts the Editor
    root.mainloop()