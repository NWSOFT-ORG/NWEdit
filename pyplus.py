#!/usr/local/bin/python3.9
# coding: utf-8
"""
+ =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-= +
| pyplus.py -- the editor's ONLY file                 |
| The somehow-professional editor                     |
| It's extremely small! (around 80 kB)                |
| You can visit my site for more details!             |
| +----------------------------------------------+    |
| | https://ZCG-coder.github.io/NWSOFT/PyPlusWeb |    |
| +----------------------------------------------+    |
| You can also contribute it on github!               |
| Note: Some parts are adapted from stack overflow.   |
+ =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-= +
Also, it's cross-compatible!
"""
# These modules are from the base directory
from console import *
from customenotebook import *
from dialogs import *
from statusbar import *
from treeview import *
from functions import *
from hexview import *
from tktext import *

os.chdir(APPDIR)
logger = logging.getLogger('PyPlus')
logging.basicConfig(
    filename='pyplus.log',
    filemode='w',
    level=logging.DEBUG,
    format='%(asctime)s : %(levelname)s : %(funcName)s : %(message)s')

logger.info(f'Tkinter version: {tk.TkVersion}')
logger.debug('All modules imported')


class Document:
    """Helper class, for the editor"""

    def __init__(self, frame, textbox, file_dir) -> None:
        self.frame = frame
        self.file_dir = file_dir
        self.textbox = textbox


class Editor:
    """The editor class."""

    def __init__(self, master) -> None:
        """The editor object, the entire thing that goes in the
window.
Lacks these MacOS support:
* The file selector does not work.
"""
        try:
            self.settings_class = Settings()
            self.file_settings_class = Filetype()
            self.linter_settings_class = Linter()
            self.cmd_settings_class = RunCommand()
            self.format_settings_class = FormatCommand()
            self.commet_settings_class = CommentMarker()
            self.theme = self.settings_class.get_settings('theme')
            self.tabwidth = self.settings_class.get_settings('tab')
            logger.debug('Settings loaded')

            self.master = master
            self.master.geometry('900x600')
            self.close_icon = tk.PhotoImage(file='Images/close.gif')
            self.close_icon_dark = tk.PhotoImage(file='Images/close-dark.gif')
            self.copy_icon = tk.PhotoImage(file='Images/copy.gif')
            self.cut_icon = tk.PhotoImage(file='Images/cut.gif')
            self.cut_icon = tk.PhotoImage(file='Images/cut.gif')
            self.delete_icon = tk.PhotoImage(file='Images/delete.gif')
            self.indent_icon = tk.PhotoImage(file='Images/indent.gif')
            self.lint_icon = tk.PhotoImage(file='Images/lint.gif')
            self.new_icon = tk.PhotoImage(file='Images/new.gif')
            self.open_icon = tk.PhotoImage(file='Images/open-16px.gif')
            self.paste_icon = tk.PhotoImage(file='Images/paste.gif')
            self.pyterm_icon = tk.PhotoImage(file='Images/py-term.gif')
            self.redo_icon = tk.PhotoImage(file='Images/redo.gif')
            self.reload_icon = tk.PhotoImage(file='Images/reload.gif')
            self.run_icon = tk.PhotoImage(file='Images/run-16px.gif')
            self.save_as_icon = tk.PhotoImage(file='Images/saveas-16px.gif')
            self.search_icon = tk.PhotoImage(file='Images/search.gif')
            self.term_icon = tk.PhotoImage(file='Images/term.gif')
            self.undo_icon = tk.PhotoImage(file='Images/undo.gif')
            self.unindent_icon = tk.PhotoImage(file='Images/unindent.gif')
            self.sel_all_icon = tk.PhotoImage(file='Images/sel-all.gif')
            self.format_icon = tk.PhotoImage(file='Images/format.gif')
            logger.debug('Icons loaded')
            if OSX:
                PyTouchBar.prepare_tk_windows(self.master)
                open_button = PyTouchBar.TouchBarItems.Button(
                    image='Images/open.gif', action=self._open)
                save_as_button = PyTouchBar.TouchBarItems.Button(
                    image='Images/saveas.gif', action=self.save_as)
                close_button = PyTouchBar.TouchBarItems.Button(
                    image='Images/close.gif', action=self.close_tab)
                space = PyTouchBar.TouchBarItems.Space.Flexible()
                run_button = PyTouchBar.TouchBarItems.Button(
                    image='Images/run.gif', action=self.run)
                PyTouchBar.set_touchbar([
                    open_button, save_as_button, close_button, space,
                    run_button
                ])
            ttkthemes.ThemedStyle(self.master).set_theme(self.theme)
            self.icon = tk.PhotoImage(file='Images/pyplus.gif')
            self.master.iconphoto(True, self.icon)
            # Base64 image, this probably decreases the repo size.
            logger.debug('Theme loaded')

            self.tabs = {}

            self.pandedwin = ttk.Panedwindow(self.master, orient='horizontal')
            self.pandedwin.pack(fill='both', expand=1)
            self.nb = ClosableNotebook(self.master, self.close_tab)
            self.nb.bind('<B1-Motion>', self.move_tab)
            self.nb.pack(expand=1, fill='both')
            self.filetree = FileTree(self.master, self.open_file)
            self.pandedwin.add(self.filetree)
            self.pandedwin.add(self.nb)
            self.nb.enable_traversal()

            self.master.protocol(
                'WM_DELETE_WINDOW', lambda: self.exit(force=False)
            )  # When the window is closed, or quit from Mac, do exit action
            self.master.createcommand(
                'exit', lambda: self.exit(force=False)
            )  # When the window is closed, or quit from Mac, do exit action

            menubar = tk.Menu(self.master)
            self.statusbar = Statusbar()
            # Name can be apple only, don't really know why!
            app_menu = tk.Menu(menubar, name='apple', tearoff=0)

            app_menu.add_command(label='About PyPlus', command=self._version)
            preferences = tk.Menu(app_menu, tearoff=0)
            preferences.add_command(label="General Settings",
                                    command=lambda: self.open_file(
                                        APPDIR + '/Settings/general-settings'
                                                 '.json'))
            preferences.add_command(label="Format Command Settings",
                                    command=lambda: self.open_file(
                                        APPDIR + '/Settings/format-settings'
                                                 '.json'))
            preferences.add_command(label="Lexer Settings",
                                    command=lambda: self.open_file(
                                        APPDIR + '/Settings/lexer-settings'
                                                 '.json'))
            preferences.add_command(label="Linter Settings",
                                    command=lambda: self.open_file(
                                        APPDIR + '/Settings/linter-settings'
                                                 '.json'))
            preferences.add_command(label="Run Command Settings",
                                    command=lambda: self.open_file(
                                        APPDIR + '/Settings/cmd-settings'
                                                 '.json'))
            preferences.add_separator()
            preferences.add_command(label='Backup Settings to...',
                                    command=self.settings_class.zip_settings)
            preferences.add_command(label='Load Settings from...',
                                    command=self.settings_class.unzip_settings)
            app_menu.add_cascade(label="Preferences", menu=preferences)
            app_menu.add_separator()
            app_menu.add_command(label='Exit Editor', command=self.exit)
            app_menu.add_command(label='Restart app', command=self.restart)
            app_menu.add_command(label='Check for updates',
                                 command=self.check_updates)

            filemenu = tk.Menu(menubar, tearoff=0)
            filemenu.add_command(label='New...',
                                 command=self.filetree.new_file,
                                 compound='left',
                                 accelerator=f'{MAIN_KEY}-n',
                                 image=self.new_icon)
            filemenu.add_command(label='Open File',
                                 command=self.open_file,
                                 accelerator=f'{MAIN_KEY}-o',
                                 compound='left',
                                 image=self.open_icon)
            filemenu.add_command(label='Save Copy to...',
                                 command=self.save_as,
                                 accelerator=f'{MAIN_KEY}-Shift-S',
                                 compound='left',
                                 image=self.save_as_icon)
            filemenu.add_command(label='Close Tab',
                                 command=self.close_tab,
                                 accelerator=f'{MAIN_KEY}-w',
                                 compound='left',
                                 image=self.close_icon)
            filemenu.add_command(label='Reload all files from disk',
                                 command=self.reload,
                                 accelerator=f'{MAIN_KEY}-r',
                                 compound='left',
                                 image=self.reload_icon)

            editmenu = tk.Menu(menubar, tearoff=0)
            editmenu.add_command(label='Undo',
                                 command=self.undo,
                                 accelerator=f'{MAIN_KEY}-z',
                                 compound='left',
                                 image=self.undo_icon)
            editmenu.add_command(label='Redo',
                                 command=self.redo,
                                 accelerator=f'{MAIN_KEY}-Shift-z',
                                 compound='left',
                                 image=self.redo_icon)
            editmenu.add_separator()
            editmenu.add_command(label='Cut',
                                 command=self.cut,
                                 accelerator=f'{MAIN_KEY}-x',
                                 compound='left',
                                 image=self.cut_icon)
            editmenu.add_command(label='Copy',
                                 command=self.copy,
                                 accelerator=f'{MAIN_KEY}-c',
                                 compound='left',
                                 image=self.copy_icon)
            editmenu.add_command(label='Paste',
                                 command=self.paste,
                                 accelerator=f'{MAIN_KEY}-v',
                                 compound='left',
                                 image=self.paste_icon)
            editmenu.add_command(label='Delete Selected',
                                 compound='left',
                                 image=self.delete_icon,
                                 command=self.delete)
            editmenu.add_command(label='Duplicate Line or Selected',
                                 command=self.duplicate_line)
            editmenu.add_command(label='Select All',
                                 command=self.select_all,
                                 accelerator=f'{MAIN_KEY}-a',
                                 compound='left',
                                 image=self.sel_all_icon)

            self.codemenu = tk.Menu(menubar, tearoff=0)
            self.codemenu.add_command(label='Indent',
                                      command=lambda: self.indent('indent'),
                                      accelerator=f'{MAIN_KEY}-i',
                                      compound='left',
                                      image=self.indent_icon)
            self.codemenu.add_command(label='Unident',
                                      command=lambda: self.indent('unindent'),
                                      accelerator=f'{MAIN_KEY}-u',
                                      compound='left',
                                      image=self.unindent_icon)
            self.codemenu.add_separator()
            self.codemenu.add_command(
                label='Comment/Uncomment Line or Selected',
                command=self.comment_lines)
            self.codemenu.add_separator()
            self.codemenu.add_command(label='Run',
                                      command=self.run,
                                      accelerator=f'{MAIN_KEY}-b',
                                      compound='left',
                                      image=self.run_icon)
            self.codemenu.add_command(label='Lint',
                                      command=self.lint_source,
                                      compound='left',
                                      image=self.lint_icon)
            self.codemenu.add_command(label='Auto-format',
                                      command=self.autopep,
                                      compound='left',
                                      image=self.format_icon)
            self.codemenu.add_separator()
            self.codemenu.add_command(label='Find and replace',
                                      command=self.search,
                                      accelerator=f'{MAIN_KEY}-f',
                                      compound='left',
                                      image=self.search_icon)
            self.codemenu.add_command(label='Bigger view',
                                      command=self.biggerview)
            self.codemenu.add_separator()
            self.codemenu.add_command(label='Open Python Shell',
                                      command=self.python_shell,
                                      compound='left',
                                      image=self.pyterm_icon)
            self.codemenu.add_command(label='Open System Shell',
                                      command=self.system_shell,
                                      compound='left',
                                      image=self.term_icon)

            navmenu = tk.Menu(menubar, tearoff=0)
            navmenu.add_command(label='Go to ...',
                                command=self.goto,
                                accelerator=f'{MAIN_KEY}-Shift-N')
            navmenu.add_command(label='-1 char', command=self.nav_1cb)
            navmenu.add_command(label='+1 char', command=self.nav_1cf)
            navmenu.add_command(label='Word end', command=self.nav_wordend)
            navmenu.add_command(label='Word start', command=self.nav_wordstart)
            navmenu.add_command(label='Select word', command=self.sel_word)
            gitmenu = tk.Menu(menubar, tearoff=0)
            gitmenu.add_command(label='Initialize',
                                command=lambda: self.git('init'))
            gitmenu.add_command(label='Add all',
                                command=lambda: self.git('addall'))
            gitmenu.add_command(label='Add selected',
                                command=lambda: self.git('addsel'))
            gitmenu.add_command(label='Commit',
                                command=lambda: self.git('commit'))
            gitmenu.add_command(label='Clone',
                                command=lambda: self.git('clone'))
            gitmenu.add_command(label='Other',
                                command=lambda: self.git('other'))

            menubar.add_cascade(label='PyPlus', menu=app_menu)  # App menu
            menubar.add_cascade(label='File', menu=filemenu)
            menubar.add_cascade(label='Edit', menu=editmenu)
            menubar.add_cascade(label='Code', menu=self.codemenu)
            menubar.add_cascade(label='Navigate', menu=navmenu)
            menubar.add_cascade(label='Git', menu=gitmenu)
            self.master.config(menu=menubar)
            logger.debug('Menu created')
            self.right_click_menu = tk.Menu(self.master, tearoff=0)
            self.right_click_menu.add_command(label='Undo', command=self.undo)
            self.right_click_menu.add_command(label='Redo', command=self.redo)
            self.right_click_menu.add_separator()
            self.right_click_menu.add_command(label='Cut', command=self.cut)
            self.right_click_menu.add_command(label='Copy', command=self.copy)
            self.right_click_menu.add_command(label='Paste',
                                              command=self.paste)
            self.right_click_menu.add_command(label='Delete',
                                              command=self.delete)
            self.right_click_menu.add_separator()
            self.right_click_menu.add_command(label='Select All',
                                              command=self.select_all)
            logger.debug('Right-click menu created')

            # Keyboard bindings
            self.master.bind(f'<{MAIN_KEY}-w>', self.close_tab)
            self.master.bind(f'<{MAIN_KEY}-o>', self._open)
            logger.debug('Bindings created')

            self.master.bind("<<MouseEvent>>", self.mouse)
            self.master.event_add("<<MouseEvent>>", "<ButtonRelease>")
            self.start_screen()
            self.master.focus_force()
            self.update_title()
            self.update_statusbar()
            with open('recent_files.txt') as f:
                for line in f.read().split('\n'):
                    if line != '':
                        self.open_file(line)
        except Exception:
            logger.exception('Error when initializing:')
            with open('recent_files.txt', 'w') as f:
                f.write('')

    def start_screen(self) -> None:
        first_tab = tk.Canvas(self.nb, background='white')
        first_tab.create_image(20, 20, anchor='nw', image=self.icon)
        first_tab.create_text(60,
                              10,
                              anchor='nw',
                              text='Welcome to PyPlus!',
                              font='Arial 50',
                              fill='black')
        label1 = ttk.Label(first_tab,
                           text='Open file',
                           foreground='blue',
                           background='white',
                           cursor='hand2',
                           compound='left',
                           image=self.open_icon)
        label2 = ttk.Label(first_tab,
                           text='New...',
                           foreground='blue',
                           background='white',
                           cursor='hand2',
                           compound='left',
                           image=self.new_icon)
        label3 = ttk.Label(first_tab,
                           text='Clone',
                           foreground='blue',
                           background='white',
                           cursor='hand2')
        label4 = ttk.Label(first_tab,
                           text='Exit',
                           foreground='blue',
                           background='white',
                           cursor='hand2',
                           compound='left',
                           image=self.close_icon_dark)
        label1.bind('<Button>', self._open)
        label2.bind('<Button>', self.filetree.new_file)
        label4.bind('<Button>', lambda _=None: self.exit(force=True))
        label3.bind('<Button>', lambda _=None: self.git('clone'))

        first_tab.create_window(50, 100, window=label1, anchor='nw')
        first_tab.create_window(50, 140, window=label2, anchor='nw')
        first_tab.create_window(50, 180, window=label3, anchor='nw')
        first_tab.create_window(50, 220, window=label4, anchor='nw')
        self.nb.add(first_tab, text='Start')
        logger.debug('Start screen created')

    def create_text_widget(self, frame: ttk.Frame) -> EnhancedTextFrame:
        """Creates a text widget in a frame."""

        def tab(event=None):
            event.widget.edit_separator()
            event.widget.insert('insert',
                                ' ' * self.tabwidth)  # Convert tabs to spaces
            self.key()
            event.widget.edit_separator()
            # Quit quickly, before a char is being inserted.
            return 'break'

        panedwin = ttk.Panedwindow(frame)
        panedwin.pack(fill='both', expand=1)

        textframe = EnhancedTextFrame(panedwin)
        # The one with line numbers and a nice dark theme
        textframe.pack(fill='both', expand=1, side='right')
        panedwin.add(textframe)
        textframe.panedwin = panedwin
        textframe.set_first_line(1)

        textbox = textframe.text  # text widget
        textbox.frame = frame  # The text will be packed into the frame.
        textbox.bind(('<Button-2>' if OSX else '<Button-3>'), self.right_click)
        textbox.bind('<BackSpace>', self.backspace)
        textbox.bind('<Return>', self.autoindent)
        textbox.bind('<Tab>', tab)
        textbox.bind(f'<{MAIN_KEY}-b>', self.run)
        textbox.bind(f'<{MAIN_KEY}-f>', self.search)
        textbox.bind(f'<{MAIN_KEY}-i>', lambda _=None: self.indent('indent'))
        textbox.bind(f'<{MAIN_KEY}-n>', self.filetree.new_file)
        textbox.bind(f'<{MAIN_KEY}-N>', self.goto)
        textbox.bind(f'<{MAIN_KEY}-r>', self.reload)
        textbox.bind(f'<{MAIN_KEY}-S>', self._saveas)
        textbox.bind(f'<{MAIN_KEY}-u>', lambda _=None: self.indent('unindent'))
        textbox.bind(f'<{MAIN_KEY}-Z>', self.redo)
        textbox.bind(f'<{MAIN_KEY}-z>', self.undo)
        textbox.bind('<<Key>>', self.key)
        textbox.event_add('<<Key>>', '<KeyRelease>')
        for char in ['"', "'", '(', '[', '{']:
            textbox.bind(char, self.autoinsert)
        for char in [')', ']', '}']:
            textbox.bind(char, self.close_brackets)
        textbox.focus_set()
        logger.debug('Textbox created')
        return textbox

    def update_title(self, _=None) -> str:
        try:
            if not self.tabs:
                self.master.title('PyPlus -- No file open')
                logger.debug('update_title: No file open')
                return "break"
            self.master.title(
                f'PyPlus -- {self.tabs[self.get_tab()].file_dir}')
            logger.debug('update_title: OK')
            return 'break'
        except Exception:
            self.master.title(f'PyPlus')
            return 'break'

    def update_statusbar(self, _=None) -> str:
        try:
            if not self.tabs:
                self.statusbar.label2.config(text='No file open |')
                self.statusbar.label3.config(text='')
                logger.debug('update_statusbar: No file open')
                return "break"
            currtext = self.tabs[self.get_tab()].textbox
            index = currtext.index('insert')
            ln = index.split('.')[0]
            col = index.split('.')[1]
            self.statusbar.label2.config(
                text=f'{self.tabs[self.get_tab()].file_dir} |')
            self.statusbar.label3.config(text=f'Line {ln} Col {col}')
            logger.debug('update_statusbar: OK')
            return 'break'
        except Exception:
            return 'break'

    def key(self, _=None) -> None:
        """Event when a key is pressed."""
        try:
            currtext = self.tabs[self.get_tab()].textbox
            self.recolorize(currtext)
            currtext.edit_separator()
            currtext.see('insert')
            # Auto-save
            self.save_file()
            self.update_statusbar()
            # Update statusbar and title bar
            self.update_title()
            logger.debug('update_title: OK')
        except KeyError:
            self.master.bell()
            logger.exception('Error when handling keyboard event:')

    def mouse(self, _=None) -> None:
        """The action done when the mouse is clicked"""
        try:
            self.update_statusbar()
            # Update statusbar and title bar
            self.update_title()
            logger.debug('update_title: OK')
        except KeyError:
            self.master.bell()
            logger.exception('Error when handling mouse event:')

    def create_tags(self, textbox: EnhancedText) -> None:
        """
The method creates the tags associated with each distinct style element of the
source code 'dressing'
"""
        currtext = textbox
        bold_font = font.Font(currtext, currtext.cget("font"))
        bold_font.configure(weight=font.BOLD)
        italic_font = font.Font(currtext, currtext.cget("font"))
        italic_font.configure(slant=font.ITALIC)
        bold_italic_font = font.Font(currtext, currtext.cget("font"))
        bold_italic_font.configure(weight=font.BOLD, slant=font.ITALIC)
        style = get_style_by_name(self.settings_class.get_settings('pygments'))

        for ttype, ndef in style:
            tag_font = None

            if ndef['bold'] and ndef['italic']:
                tag_font = bold_italic_font
            elif ndef['bold']:
                tag_font = bold_font
            elif ndef['italic']:
                tag_font = italic_font

            if ndef['color']:
                foreground = "#%s" % ndef['color']
            else:
                foreground = None

            currtext.tag_configure(str(ttype),
                                   foreground=foreground,
                                   font=tag_font)

    def recolorize(self, textbox: EnhancedText) -> None:
        """
This method colors and styles the prepared tags
"""
        try:
            self.create_tags(textbox)
            currtext = textbox
            _code = currtext.get("1.0", "end-1c")
            tokensource = currtext.lexer.get_tokens(_code)
            start_line = 1
            start_index = 0
            end_line = 1
            end_index = 0

            for ttype, value in tokensource:
                if "\n" in value:
                    end_line += value.count("\n")
                    end_index = len(value.rsplit("\n", 1)[1])
                else:
                    end_index += len(value)

                if value not in (" ", "\n"):
                    index1 = f"{start_line}.{start_index}"
                    index2 = f"{end_line}.{end_index}"

                    for tagname in currtext.tag_names(index1):
                        if tagname != 'sel':
                            currtext.tag_remove(tagname, index1, index2)

                    currtext.tag_add(str(ttype), index1, index2)

                start_line = end_line
                start_index = end_index
                currtext.tag_configure('sel', foreground='black')

            currtext.update()  # Have to update
        except Exception as e:
            print(e)

    def open_file(self, file='') -> None:
        """Opens a file
If a file is not provided, a messagebox'll
pop up to ask the user to select the path.
"""
        if file:
            file_dir = file
        else:
            file_dir = ''
            FileOpenDialog(self.open_file)

        if file_dir:
            try:  # If the file is in binary, ask the user to open in Hex editor
                for tab in self.tabs.items():
                    if file_dir == tab[1].file_dir:
                        self.nb.select(tab[1].frame)
                        return
                if is_binary_string(open(file_dir, 'rb').read()):
                    dialog = MessageYesNoDialog(self.master, 'Error',
                                                'View in Hex?')
                    if dialog.result:
                        logger.info('HexView: opened')
                        viewer = ttk.Frame(self.master)
                        viewer.focus_set()
                        window = HexView(viewer)
                        window.open(file_dir)
                        self.tabs[viewer] = Document(viewer, window.textbox,
                                                     file_dir)
                        self.nb.add(viewer, text=f'Hex -- {file_dir}')
                        self.nb.select(viewer)
                        return
                    else:
                        logging.info('User pressed No.')
                        return
                file = open(file_dir)
                extens = file_dir.split('.')[-1]

                new_tab = ttk.Frame(self.nb)
                textbox = self.create_text_widget(new_tab)
                self.tabs[new_tab] = Document(new_tab, textbox, file_dir)
                self.nb.add(new_tab, text=os.path.basename(file_dir))
                self.nb.select(new_tab)
                shell_frame = ttk.Frame(new_tab)
                ttkthemes.ThemedStyle(shell_frame).set_theme(self.theme)
                main_window = Console(shell_frame, None, shell_frame.destroy)
                main_window.pack(fill=tk.BOTH, expand=True)

                # Puts the contents of the file into the text widget.
                currtext = self.tabs[new_tab].textbox
                currtext.insert('end',
                                file.read().replace('\t', ' ' * self.tabwidth))
                # Inserts file content, replacing tabs with four spaces
                currtext.focus_set()
                currtext.set_lexer(
                    self.file_settings_class.get_lexer_settings(extens))
                currtext.lint_cmd = self.linter_settings_class.get_linter_settings(
                    extens)
                currtext.cmd = self.cmd_settings_class.get_command_settings(
                    extens)
                currtext.format_command = self.format_settings_class.get_command_settings(
                    extens)
                currtext.comment_marker = self.commet_settings_class.get_comment_settings(
                    extens)
                currtext.see('insert')
                currtext.event_generate('<<Key>>')
                currtext.focus_set()
                currtext.master.on_change()
                logging.info('File opened')
                return
            except Exception as e:
                if type(e).__name__ != "ValueError":
                    logger.exception('Error when opening file:')
                else:
                    logger.exception(f'Warning! Program has ValueError: {e}')

    def _open(self, _=None) -> None:
        """This method just prompts the user to open a file when C-O is pressed"""
        self.open_file()

    def save_as(self, file_dir=None) -> None:
        if self.tabs:
            if file_dir:
                file_dir = file_dir
            else:
                file_dir = ''
                FileSaveAsDialog(self.save_as)
            curr_tab = self.get_tab()
            if not file_dir:
                return

            self.tabs[curr_tab].file_dir = file_dir
            self.nb.tab(curr_tab, text=os.path.basename(file_dir))
            with open(file_dir, 'w') as f:
                f.write(self.tabs[curr_tab].textbox.get(1.0, 'end'))
            self.update_title()
            self.reload()

    def _saveas(self, _=None):
        self.save_as()

    def save_file(self, _=None) -> None:
        """Saves an *existing* file"""
        try:
            curr_tab = self.get_tab()
            if not os.path.exists(self.tabs[curr_tab].file_dir):
                self.save_as()
                return
            if os.access(self.tabs[curr_tab].file_dir, os.W_OK):
                with open(self.tabs[curr_tab].file_dir, 'w') as file:
                    file.write(self.tabs[curr_tab].textbox.get(1.0,
                                                               'end').strip())
            else:
                ErrorDialog(self.master, 'File read only')
        except Exception:
            pass

    def copy(self) -> None:
        try:
            sel = self.tabs[self.get_tab()].textbox.get(
                tk.SEL_FIRST, tk.SEL_LAST)
            self.tabs[self.get_tab()].textbox.clipboard_clear()
            self.tabs[self.get_tab()].textbox.clipboard_append(sel)
        except Exception:
            pass

    def delete(self) -> None:
        try:
            self.tabs[self.get_tab()].textbox.delete(tk.SEL_FIRST, tk.SEL_LAST)
            self.key()
        except Exception:
            pass

    def cut(self) -> None:
        try:
            currtext = self.tabs[self.get_tab()].textbox
            currtext.edit_separator()
            sel = currtext.get(tk.SEL_FIRST, tk.SEL_LAST)
            currtext.clipboard_clear()
            currtext.clipboard_append(sel)
            currtext.delete(tk.SEL_FIRST, tk.SEL_LAST)
            currtext.edit_separator()
            self.key()
        except Exception as e:
            print(e)

    def paste(self) -> None:
        try:
            clipboard = self.tabs[self.get_tab()].textbox.clipboard_get()
            self.tabs[self.get_tab()].textbox.edit_separator()
            if clipboard:
                self.tabs[self.get_tab()].textbox.insert(
                    'insert', clipboard.replace('\t', ' ' * self.tabwidth))
            self.key()
            self.tabs[self.get_tab()].textbox.edit_separator()
        except Exception:
            pass

    def select_all(self) -> None:
        try:
            curr_tab = self.get_tab()
            self.tabs[curr_tab].textbox.tag_add(tk.SEL, '1.0', tk.END)
            self.tabs[curr_tab].textbox.mark_set(tk.INSERT, tk.END)
            self.tabs[curr_tab].textbox.see(tk.INSERT)
        except Exception:
            pass

    def duplicate_line(self) -> None:
        if not self.tabs:
            return
        currtext = self.tabs[self.get_tab()].textbox
        currtext.edit_separator()
        sel = currtext.get(tk.SEL_FIRST, tk.SEL_LAST)
        if currtext.tag_ranges('sel'):
            currtext.tag_remove('sel', '1.0', 'end')
            currtext.insert('insert', sel)
        else:
            text = currtext.get('insert linestart', 'insert lineend')
            currtext.insert('insert', '\n' + text)
        currtext.edit_separator()
        self.key()

    def run(self, _=None) -> None:
        """Runs the file
Steps:
1) Writes run code into the batch file.
2) Linux only: uses chmod to make the sh execuable
3) Runs the run file"""
        try:
            if WINDOWS:  # Windows
                with open(APPDIR + '/run.bat', 'w') as f:
                    f.write((RUN_BATCH.format(
                        dir=APPDIR,
                        file=self.tabs[self.get_tab()].file_dir,
                        cmd=self.tabs[self.get_tab()].textbox.cmd)))
                run_in_terminal('run.bat && del run.bat && exit', cwd=APPDIR)
            else:  # Others
                with open(APPDIR + '/run.sh', 'w') as f:
                    f.write((RUN_BATCH.format(
                        dir=APPDIR,
                        file=self.tabs[self.get_tab()].file_dir,
                        cmd=self.tabs[self.get_tab()].textbox.cmd,
                        script_dir=Path(
                            self.tabs[self.get_tab()].file_dir).parent)))
                run_in_terminal(
                    'chmod 700 run.sh && ./run.sh && rm run.sh',
                    cwd=APPDIR)
        except Exception:
            ErrorDialog(self.master, 'This language is not supported.')

    @staticmethod
    def system_shell() -> None:
        open_system_shell()

    def python_shell(self) -> None:
        shell_frame = tk.Toplevel(self.master)
        ttkthemes.ThemedStyle(shell_frame).set_theme(self.theme)
        main_window = Console(shell_frame, None, shell_frame.destroy)
        main_window.text.lexer = lexers.get_lexer_by_name('pycon')
        main_window.text.focus_set()
        self.recolorize(main_window.text)
        main_window.text.bind('<KeyRelease>',
                              lambda _=None: self.recolorize(main_window.text))
        main_window.pack(fill='both', expand=1)
        shell_frame.mainloop()

    def backspace(self, _=None) -> None:
        if not self.tabs:
            return
        currtext = self.tabs[self.get_tab()].textbox
        currtext.edit_separator()
        # Backchar
        if currtext.get('insert -1c',
                        'insert +1c') in ['\'\'', '""', '[]', '{}', '()']:
            currtext.delete('insert', 'insert +1c')
        # Backtab
        if currtext.get(f'insert -{self.tabwidth}c',
                        'insert') == ' ' * self.tabwidth:
            currtext.delete(f'insert -{self.tabwidth - 1}c', 'insert')
        self.key()
        currtext.edit_separator()

    def close_brackets(self, _=None) -> str:
        if not self.tabs:
            return 'notabs'
        currtext = self.tabs[self.get_tab()].textbox
        if currtext.get('insert', 'insert +1c') in [')', ']', '}', '\'', '"']:
            currtext.mark_set('insert', 'insert +1c')
            self.key()
            return 'break'
        currtext.edit_separator()
        self.key()

    def autoinsert(self, event=None) -> str:
        """Auto-inserts a symbol
* ' -> ''
* " -> ""
* ( -> ()
* [ -> []
* { -> {}"""
        if not self.tabs:
            return 'notabs'
        currtext = self.tabs[self.get_tab()].textbox
        currtext.edit_separator()
        char = event.char
        if currtext.tag_ranges('sel'):
            selected = currtext.get('sel.first', 'sel.last')
            if char == "'":
                currtext.delete('sel.first', 'sel.last')
                currtext.insert('insert', f"'{selected}'")
                return 'break'
            if char == '"':
                currtext.delete('sel.first', 'sel.last')
                currtext.insert('insert', f'"{selected}"')
                return 'break'
            if char == "(":
                currtext.delete('sel.first', 'sel.last')
                currtext.insert('insert', f"({selected})")
                return 'break'
            if char == "[":
                currtext.delete('sel.first', 'sel.last')
                currtext.insert('insert', f"[{selected}]")
                return 'break'
            if char == "{":
                currtext.delete('sel.first', 'sel.last')
                currtext.insert('insert', "{" + selected +
                                "}")  # Can't use f-string for this!
                return 'break'

        if char == '\'':
            if currtext.get('insert', 'insert +1c') == "'":
                currtext.mark_set('insert', 'insert +1c')
                return 'break'
            currtext.insert('insert', '\'\'')
            currtext.mark_set('insert', 'insert -1c')
            return 'break'
        elif char == '"':
            if currtext.get('insert', 'insert +1c') == '"':
                currtext.mark_set('insert', 'insert +1c')
                return 'break'
            currtext.insert('insert', '""')
            currtext.mark_set('insert', 'insert -1c')
            return 'break'
        elif char == '(':
            currtext.insert('insert', ')')
        elif char == '[':
            currtext.insert('insert', ']')
        elif char == '{':
            currtext.insert('insert', '}')
        currtext.mark_set('insert', 'insert -1c')
        currtext.edit_separator()
        self.key()

    def autoindent(self, _=None) -> str:
        """Auto-indents the next line"""
        currtext = self.tabs[self.get_tab()].textbox
        currtext.edit_separator()
        indentation = ""
        lineindex = currtext.index("insert").split(".")[0]
        linetext = currtext.get(lineindex + ".0", lineindex + ".end")
        for character in linetext:
            if character in [" ", "\t"]:
                indentation += character
            else:
                break

        if linetext.endswith(":"):
            indentation += " " * self.tabwidth
        if linetext.endswith("\\"):
            indentation += " " * self.tabwidth
        if 'return' in linetext or 'break' in linetext:
            indentation = indentation[4:]
        if linetext.endswith('(') or linetext.endswith(
                ', ') or linetext.endswith(','):
            indentation += " " * self.tabwidth

        currtext.insert(currtext.index("insert"), "\n" + indentation)
        currtext.edit_separator()
        self.key()
        return "break"

    def search(self, _=None) -> None:
        global case
        global regexp
        global start, end
        global starts
        if not self.tabs:
            return
        case = tk.BooleanVar()
        regexp = tk.BooleanVar()
        start = tk.SEL_FIRST
        end = tk.SEL_LAST
        currtext = self.tabs[self.get_tab()].textbox
        if not currtext.tag_ranges('sel'):
            start = tk.FIRST
            end = tk.END
        starts = []
        search_frame = ttk.Frame(self.tabs[self.get_tab()].textbox.frame)
        style = ThemedStyle(search_frame)
        style.set_theme(self.theme)

        search_frame.pack(anchor='nw', side='bottom')
        ttk.Label(search_frame, text='Search: ').pack(side='left',
                                                      anchor='nw',
                                                      fill='y')
        content = tk.Entry(search_frame,
                           background='black',
                           foreground='white',
                           insertbackground='white',
                           highlightthickness=0)
        content.pack(side='left', fill='both')

        forward = ttk.Button(search_frame, text='<', width=1)
        forward.pack(side='left')

        backward = ttk.Button(search_frame, text='>', width=1)
        backward.pack(side='left')

        ttk.Label(search_frame, text='Replacement: ').pack(side='left',
                                                           anchor='nw',
                                                           fill='y')
        repl = tk.Entry(search_frame,
                        background='black',
                        foreground='white',
                        insertbackground='white',
                        highlightthickness=0)
        repl.pack(side='left', fill='both')

        repl_button = ttk.Button(search_frame, text='Replace all')
        repl_button.pack(side='left')
        clear_button = ttk.Button(search_frame, text='Clear All')
        clear_button.pack(side='left')

        case_yn = ttk.Checkbutton(search_frame,
                                  text='Case Sensitive',
                                  variable=case)
        case_yn.pack(side='left')

        reg_button = ttk.Checkbutton(search_frame,
                                     text='RegExp',
                                     variable=regexp)
        reg_button.pack(side='left')

        def find(_=None):
            global starts
            found = tk.IntVar()
            text = self.tabs[self.get_tab()].textbox
            text.tag_remove('found', '1.0', 'end')
            s = content.get()
            starts.clear()
            if s != '\\' and s:
                idx = '1.0'
                while 1:
                    idx = text.search(s,
                                      idx,
                                      nocase=not (case.get()),
                                      stopindex='end',
                                      regexp=regexp.get(),
                                      count=found)
                    if not idx:
                        break
                    lastidx = '%s+%dc' % (idx, len(s))
                    text.tag_add('found', idx, lastidx)
                    starts.append(idx)
                    text.mark_set('insert', idx)
                    text.focus_set()
                    idx = lastidx
                text.tag_config('found', foreground='red', background='yellow')
            text.see('insert')
            text.statusbar.config(text=f'Found {found.get()} matches')

        def replace():
            text = self.tabs[self.get_tab()].textbox
            text.tag_remove('found', '1.0', 'end')
            s = content.get()
            r = repl.get()
            if s != '\\' and s:
                idx = '1.0'
                while 1:
                    idx = text.search(s,
                                      idx,
                                      nocase=not (case.get()),
                                      stopindex='end',
                                      regexp=regexp.get())
                    if not idx:
                        break
                    lastidx = '%s+%dc' % (idx, len(s))
                    text.delete(idx, lastidx)
                    text.insert(idx, r)
                    idx = lastidx

        def clear():
            text = self.tabs[self.get_tab()].textbox
            text.tag_remove('found', '1.0', 'end')

        def nav_forward():
            try:
                global starts
                text = self.tabs[self.get_tab()].textbox
                curpos = text.index('insert')
                if curpos in starts:
                    prev = starts.index(curpos) - 1
                    text.mark_set('insert', starts[prev])
                    text.see('insert')
                    text.focus_set()
            except Exception:
                pass

        def nav_backward():
            try:
                global starts
                text = self.tabs[self.get_tab()].textbox
                curpos = text.index('insert')
                if curpos in starts:
                    prev = starts.index(curpos) + 1
                    text.mark_set('insert', starts[prev])
                    text.see('insert')
                    text.focus_set()
            except Exception:
                pass

        clear_button.config(command=clear)
        repl_button.config(command=replace)
        forward.config(command=nav_forward)
        backward.config(command=nav_backward)
        content.bind('<KeyRelease>', find)

        def _exit():
            search_frame.pack_forget()
            clear()
            self.tabs[self.get_tab()].textbox.focus_set()

        ttk.Button(search_frame, text='x', command=_exit,
                   width=1).pack(side='right', anchor='ne')

    def undo(self, _=None) -> None:
        try:
            self.tabs[self.get_tab()].textbox.edit_undo()
        except Exception:
            pass

    def redo(self, _=None) -> None:
        try:
            self.tabs[self.get_tab()].textbox.edit_redo()
        except Exception:
            pass

    def right_click(self, event: tk.EventType) -> None:
        self.right_click_menu.post(event.x_root, event.y_root)

    def close_tab(self, event=None) -> None:
        global selected_tab
        try:
            if self.nb.index("end"):
                # Close the current tab if close is selected from file menu, or
                # keyboard shortcut.
                if event is None or event.type == str(2):
                    selected_tab = self.get_tab()
                # Otherwise close the tab based on coordinates of center-click.
                else:
                    try:
                        index = event.widget.index('@%d,%d' %
                                                   (event.x, event.y))
                        selected_tab = self.nb.nametowidget(
                            self.nb.tabs()[index])
                    except tk.TclError:
                        return

            self.nb.forget(selected_tab)
            self.tabs.pop(selected_tab)
            self.mouse()
        except Exception:
            pass

    def reload(self) -> None:
        if not self.tabs:
            return
        tabs = []
        curr = self.nb.index(self.nb.select())
        self.nb.select(self.nb.index('end') - 1)
        for value in self.tabs.items():
            tabs.append(value[1])
        files = []
        for tab in tabs:
            files.append(tab.file_dir)
            self.close_tab()
        for x in files:
            self.open_file(x)
        self.nb.select(curr)

    def exit(self, force=False) -> None:
        if not force:
            with open('recent_files.txt', 'w') as f:
                file_list = ''
                for tab in self.tabs.values():
                    file_list += tab.file_dir + '\n'
                f.write(file_list)
            self.master.destroy()
            logger.info('Window is destroyed')
        else:
            sys.exit(0)

    def restart(self) -> None:
        self.exit(force=False)
        newtk = tk.Tk()
        self.__init__(newtk)
        newtk.mainloop()

    def get_tab(self) -> tk.Misc:
        return self.nb.nametowidget(self.nb.select())

    def move_tab(self, event: tk.EventType) -> None:
        if self.nb.index('end') > 1:
            y = self.get_tab().winfo_y() - 5

            try:
                self.nb.insert(event.widget.index('@%d,%d' % (event.x, y)),
                               self.nb.select())
            except tk.TclError:
                return

    def _version(self) -> None:
        """Shows the version and related info of the editor."""
        ver = tk.Toplevel()
        ver.resizable(0, 0)
        ver.title('About PyPlus')
        ttk.Label(ver, image=self.icon).pack(fill='both')
        ttk.Label(ver, text=f'Version {VERSION}',
                  font='Arial 30 bold').pack(fill='both')
        if self.check_updates(popup=False)[0]:
            update = ttk.Label(ver,
                               text='Updates available',
                               foreground="blue",
                               cursor="hand2")
            update.pack(fill='both')
            update.bind(
                "<Button-1>", lambda e: webbrowser.open_new_tab(
                    self.check_updates(popup=False)[1]))
        else:
            ttk.Label(ver, text='No updates available').pack(fill='both')
        ver.mainloop()

    def lint_source(self) -> None:
        if not self.tabs:
            return
        try:
            if self.tabs[self.get_tab()].textbox.lint_cmd:
                currdir = self.tabs[self.get_tab()].file_dir
                if WINDOWS:
                    with open('lint.bat', 'w') as f:
                        f.write(
                            LINT_BATCH.format(cmd=self.tabs[
                                self.get_tab()].textbox.lint_cmd))
                    subprocess.Popen(f'lint.bat "{currdir}"', shell=True)
                    os.remove('lint.bat')
                else:
                    with open('lint.sh', 'w') as f:
                        f.write(
                            LINT_BATCH.format(cmd=self.tabs[
                                self.get_tab()].textbox.lint_cmd))
                    subprocess.Popen(
                        f'chmod 700 lint.sh && ./lint.sh "{currdir}"',
                        shell=True)
                    os.remove('lint.sh')
                self.open_file('results.txt')
                os.remove('results.txt')
        except Exception:
            ErrorDialog(self.master, 'This language is not supported')
            return

    def autopep(self) -> None:
        """Auto Pretty-Format the document"""
        try:
            currtext = self.tabs[self.get_tab()].textbox
            currtext.edit_separator()
            currdir = self.tabs[self.get_tab()].file_dir
            if currtext.format_command:
                subprocess.Popen(
                    f'{currtext.format_command} "{currdir}" > {os.devnull}',
                    shell=True)  # Throw the autopep8 results into the bit bin.(/dev/null)
            else:
                ErrorDialog(self.master, 'Language not supported.')
                return
            self.reload()
            currtext.edit_separator()
        except Exception:
            logger.exception('Error when formatting:')

    def goto(self, _=None) -> None:
        if not self.tabs:
            return
        goto_frame = ttk.Frame(self.tabs[self.get_tab()].textbox.frame)
        style = ttkthemes.ThemedStyle(goto_frame)
        style.set_theme(self.theme)
        goto_frame.pack(anchor='nw')
        ttk.Label(goto_frame,
                  text='Go to place: [Ln].[Col] ').pack(side='left')
        place = tk.Entry(goto_frame,
                         background='black',
                         foreground='white',
                         insertbackground='white',
                         highlightthickness=0)
        place.focus_set()
        place.pack(side='left')

        def _goto():
            currtext = self.tabs[self.get_tab()].textbox
            currtext.mark_set('insert', place.get())
            currtext.see('insert')
            _exit()

        def _exit():
            goto_frame.pack_forget()
            self.tabs[self.get_tab()].textbox.focus_set()

        goto_button = ttk.Button(goto_frame, command=_goto, text='>> Go to')
        goto_button.pack(side='left')
        ttk.Button(goto_frame, text='x', command=_exit,
                   width=1).pack(side='right', anchor='se')

    def nav_1cf(self) -> None:
        currtext = self.tabs[self.get_tab()].textbox
        currtext.mark_set('insert', 'insert +1c')

    def nav_1cb(self) -> None:
        currtext = self.tabs[self.get_tab()].textbox
        currtext.mark_set('insert', 'insert -1c')

    def nav_wordstart(self) -> None:
        currtext = self.tabs[self.get_tab()].textbox
        currtext.mark_set('insert', 'insert -1c wordstart')

    def nav_wordend(self) -> None:
        currtext = self.tabs[self.get_tab()].textbox
        currtext.mark_set('insert', 'insert wordend')

    def sel_word(self) -> None:
        currtext = self.tabs[self.get_tab()].textbox
        currtext.tag_add('sel', 'insert -1c wordstart', 'insert wordend')

    def biggerview(self) -> None:
        if not self.tabs:
            return
        currtext = self.tabs[self.get_tab()].textbox
        if not currtext.tag_ranges('sel'):
            return
        selected_text = currtext.get('sel.first -1c linestart',
                                     'sel.last lineend')
        win = tk.Toplevel(self.master)
        win.resizable(0, 0)
        win.transient(self.master)
        textframe = EnhancedTextFrame(win)
        textframe.set_first_line(1)
        textframe.text.insert('insert', selected_text)
        textframe.text['state'] = 'disabled'
        textframe.text.lexer = currtext.lexer
        textframe.pack(fill='both', expand=1)
        self.recolorize(textframe.text)
        win.mainloop()

    def check_updates(self, popup=True) -> list:
        if 'DEV' in VERSION:
            ErrorDialog(self.master, "Updates aren't supported by develop builds,\n\
            since you're always on the latest version!") # If you're on the developer build, you don't need updates!
            return []
        download_file(
            url=
            "https://raw.githubusercontent.com/ZCG-coder/NWSOFT/master/PyPlusWeb/ver.json"
        )
        with open('ver.json') as f:
            newest = json.load(f)
        version = newest["version"]
        if not popup:
            os.remove('ver.json')
            return [bool(version != VERSION), newest["url"]]
        updatewin = tk.Toplevel(self.master)
        updatewin.title('Updates')
        updatewin.resizable(0, 0)
        updatewin.transient(self.master)
        ttkthemes.ThemedStyle(updatewin)
        if version != VERSION:
            ttk.Label(updatewin, text='Update available!',
                      font='Arial 30').pack(fill='both')
            ttk.Label(updatewin, text=version).pack(fill='both')
            ttk.Label(updatewin, text=newest["details"]).pack(fill='both')
            url = newest["url"]
            ttk.Button(updatewin,
                       text='Get this update',
                       command=lambda: webbrowser.open(url)).pack()
        else:
            ttk.Label(updatewin, text='No updates available',
                      font='Arial 30').pack(fill='both')
        os.remove('ver.json')
        updatewin.mainloop()

    def git(self, action=None) -> None:
        if action == 'clone':
            dialog = InputStringDialog(self.master, 'Clone', 'Remote git url:')
            url = dialog.result
            if not url:
                return
            run_in_terminal(f'git clone {url}')
            return
        if not self.tabs:
            return
        elif action is None:
            raise EditorErr('Invalid action -- ' + str(action))
        currdir = Path(self.tabs[self.get_tab()].file_dir).parent
        if action == 'init':
            run_in_terminal(
                cwd=currdir,
                cmd='git init && git add . && git commit -am \"Added files\"')
        elif action == 'addall':
            run_in_terminal(cwd=currdir,
                            cmd='git add . && git commit -am "Added files"')
        elif action == 'addsel':
            files = tkinter.filedialog.askopenfilenames(
                master=self.master,
                initialdir='/',
                title='Select files')
            if not files:
                return
            for x in files:
                run_in_terminal(cwd=currdir, cmd=f'git add {x}')
        elif action == 'commit':
            dialog = InputStringDialog(self.master, 'Commit...', 'Message:')
            message = dialog.result
            if not message:
                return
            run_in_terminal(f'git commit -am "{message}"')
        elif action == 'other':
            dialog = InputStringDialog(self.master, 'Other git actions...',
                                       'Action:')
            action = dialog.result
            if not action:
                return
            run_in_terminal(f'git {action}')

    def indent(self, action='indent') -> None:
        """Indent/unindent feature"""
        if not self.tabs:
            return
        currtext = self.tabs[self.get_tab()].textbox
        currtext.edit_separator()
        if currtext.tag_ranges('sel'):
            sel_start = currtext.index('sel.first linestart')
            sel_end = currtext.index('sel.last lineend')
        else:
            sel_start = currtext.index('insert linestart')
            sel_end = currtext.index('insert lineend')
        if action == 'indent':
            selected_text = currtext.get(sel_start, sel_end)
            indented = []
            for line in selected_text.splitlines():
                indented.append(' ' * self.tabwidth + line)
            currtext.delete(sel_start, sel_end)
            currtext.insert(sel_start, '\n'.join(indented))
            currtext.tag_remove('sel', '1.0', 'end')
            currtext.tag_add('sel', sel_start, f'{sel_end} +4c')
            self.key()
        elif action == 'unindent':
            selected_text = currtext.get(sel_start, sel_end)
            unindented = []
            for line in selected_text.splitlines():
                if line.startswith(' ' * self.tabwidth):
                    unindented.append(line[4:])
                else:
                    return
            currtext.delete(sel_start, sel_end)
            currtext.insert(sel_start, '\n'.join(unindented))
            currtext.tag_remove('sel', '1.0', 'end')
            currtext.tag_add('sel', sel_start, sel_end)
            self.key()
        else:
            raise EditorErr('Action undefined.')
        currtext.edit_separator()

    def comment_lines(self, _=None):
        try:
            currtext = self.tabs[self.get_tab()].textbox
            if not currtext.comment_marker:
                return
            if currtext.tag_ranges('sel'):
                start_index, end_index = 'sel.first linestart', 'sel.last lineend'
                for line in currtext.get(start_index, end_index).splitlines():
                    currtext.delete(start_index, end_index)
                    if line.startswith(currtext.comment_marker):
                        currtext.insert(
                            'insert',
                            f'{line[len(currtext.comment_marker):]}\n')
                    else:
                        currtext.insert('insert',
                                        f'{currtext.comment_marker}{line}\n')
            else:
                start_index, end_index = 'insert linestart', 'insert lineend'
                line = currtext.get(start_index, end_index)
                currtext.delete(start_index, end_index)
                if line.startswith(currtext.comment_marker):
                    currtext.insert(
                        'insert', f'{line[len(currtext.comment_marker):]}\n')
                else:
                    currtext.insert('insert',
                                    f'{currtext.comment_marker}{line}\n')
        except (KeyError, AttributeError):
            return


if __name__ == '__main__':
    root = tk.Tk()
    app = Editor(master=root)
    root.mainloop()
