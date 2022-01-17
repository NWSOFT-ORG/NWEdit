import importlib.util


class Plugin:
    def __init__(self, name):
        self.name = name
        self.menu = None

    def on_start(self):
        pass

    def register_menu(self, menu):
        self.menu = {'title': self.name,
                     'menu': menu}


class Loader:
    def __init__(self):
        spec = importlib.util.spec_from_file_location("module.name", "/path/to/file.py")
        plug = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(plug)
