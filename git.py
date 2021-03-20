from modules import *
from functions import *


class Git():
    def init(self, path):
        subprocess.run('git init', shell=True)

    def commit(self, message):
        subprocess.run(f'git commit -am "{message}"')

    def push(self, host):
        pass
    
    def pull(self, host):
        pass

    def commitgui(self):
        win = tk.Tk()
        win.title('Git')
        filelist = tk.Listbox(win)
        filelist.pack(side='top', fill='both')
        button_widget = ttk.Frame(win)
        commit_button = ttk.Button(button_widget, text='Commit')
        commit_button.pack(side='left')
        pull_button = ttk.Button(button_widget, text='Pull')
        pull_button.pack(side='left')
        push_button = ttk.Button(button_widget, text='Push')
        push_button.pack(side='left')
        button_widget.pack(side='bottom', )
        win.mainloop()