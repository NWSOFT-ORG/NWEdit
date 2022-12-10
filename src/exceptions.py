class WindowExistsError(Exception):
    def __init__(self):
        super().__init__("An open window still exsists. Call get_window() to get it.")


class NoWindowOpenError(Exception):
    def __init__(self):
        super().__init__("The object requested is not initalized.")


class ConfigurationForbiddenError(Exception):
    def __init__(self):
        super().__init__("Access to forbidden configuration.")


class ConfigurationRequestError(Exception):
    def __init__(self, item) -> None:
        super().__init__(f"Invalid configuration item: {item}.")
