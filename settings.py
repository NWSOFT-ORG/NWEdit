from constants import *


class Settings:
    """A class to read data to/from general-settings.json"""

    def __init__(self):
        try:
            with open(os.path.join(APPDIR, 'Settings/general-settings.json')) as f:
                self.settings = json.load(f)
            self.theme = self.settings['theme']
            self.highlight_theme = self.settings['pygments']
            self.tabwidth = self.settings['tabwidth']
            self.font = self.settings['font'].split()[0]
            self.size = self.settings['font'].split()[1]
            self.filetype = self.settings['file_types']
            return
        except Exception:
            messagebox.showerror("Error", "Setings are corrupted.")
            sys.exit(1)

    def get_settings(self, setting):
        if setting == 'font':
            return f'{self.font} {self.size}'
        elif setting == 'theme':
            return self.theme
        elif setting == 'tab':
            return self.tabwidth
        elif setting == 'pygments':
            return self.highlight_theme
        elif setting == 'file_type':
            # Always starts with ('All files', '*.* *')
            if self.filetype == 'all':
                return ('All files', '*.* *'),
            elif self.filetype == 'py':
                # Extend this list, since Python has a lot of file types
                return ('All files',
                        '*.* *'), ('Python Files',
                                   '*.py *.pyw *.pyx *.py3 *.pyi')
            elif self.filetype == 'txt':
                return ('All files', '*.* *'), ('Text documents',
                                                '*.txt *.rst')
            elif self.filetype == 'xml':
                # Extend this, since xml has a lot of usage formats
                return ('All files', '*.* *'), ('XML',
                                                '*.xml *.plist *.iml *.rss')
            else:
                if messagebox.showerror(
                        'Error', 'The settings aren\'t correct, \n\
                Now using default settings.'):
                    return (('All files', '*.* *'),)
        else:
            raise EditorErr('The setting is not defined')


class Filetype:
    def __init__(self):
        with open(os.path.join(APPDIR, "Settings/lexer-settings.json")) as f:
            all_settings = json.load(f)
        self.extens = []
        self.lexers = []
        for key, value in all_settings.items():
            self.extens.append(key)
            self.lexers.append(value)

    def get_lexer_settings(self, extension: str):
        try:
            if lexers.get_lexer_by_name(self.lexers[self.extens.index(
                    extension)]) == lexers.get_lexer_by_name('JSON'):
                return JSONLexer
            return lexers.get_lexer_by_name(
                self.lexers[self.extens.index(extension)])
        except Exception:
            return lexers.get_lexer_by_name('Text')


class Linter:
    def __init__(self):
        with open(os.path.join(APPDIR, "Settings/linter-settings.json")) as f:
            all_settings = json.load(f)
        self.extens = []
        self.linters = []
        for key, value in all_settings.items():
            self.extens.append(key)
            self.linters.append(value)

    def get_linter_settings(self, extension: str):
        try:
            if self.linters[self.extens.index(extension)] == "none":
                return None
            return self.linters[self.extens.index(extension)]
        except IndexError:
            return None


class FormatCommand:
    def __init__(self):
        with open(os.path.join(APPDIR, "Settings/format-settings.json")) as f:
            all_settings = json.load(f)
        self.extens = []
        self.format_commands = []
        for key, value in all_settings.items():
            self.extens.append(key)
            self.format_commands.append(value)

    def get_command_settings(self, extension: str):
        try:
            if self.format_commands[self.extens.index(extension)] == "none":
                return None
            return self.format_commands[self.extens.index(extension)]
        except IndexError:
            return None


class RunCommand:
    def __init__(self):
        with open(os.path.join(APPDIR, "Settings/cmd-settings.json")) as f:
            all_settings = json.load(f)
        self.extens = []
        self.commands = []
        for key, value in all_settings.items():
            self.extens.append(key)
            self.commands.append(value)

    def get_command_settings(self, extension: str):
        try:
            if self.commands[self.extens.index(extension)] == "none":
                return None
            return self.commands[self.extens.index(extension)]
        except IndexError:
            return None


class CommentMarker:
    def __init__(self):
        with open(os.path.join(APPDIR, "Settings/comment_markers.json")) as f:
            all_settings = json.load(f)
        self.extens = []
        self.comments = []
        for key, value in all_settings.items():
            self.extens.append(key)
            self.comments.append(value)

    def get_comment_settings(self, extension: str):
        try:
            if self.comments[self.extens.index(extension)] == "none":
                return None
            return self.comments[self.extens.index(extension)]
        except IndexError:
            return None
