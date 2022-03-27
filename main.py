#!/usr/bin/python3
from src import editor
from src.modules import tk
from src.constants import OSX

if __name__ == "__main__":
    if OSX:
        from Foundation import NSBundle

        bundle = NSBundle.mainBundle()
        if bundle:
            info = bundle.localizedInfoDictionary() or bundle.infoDictionary()
            if info and info['CFBundleName'] == 'Python':
                info['CFBundleName'] = "PyPlus"
    root = tk.Tk()

    editor.Editor(master=root)  # Starts the Editor
    root.mainloop()
