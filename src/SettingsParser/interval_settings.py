import json5rw as json

from src.exceptions import ConfigurationRequestError


class IntervalSettings:
    def __init__(self):
        with open("Config/defaults/interval.json") as f:
            self.settings = json.load(f)
        with open("Config/interval.json") as f:
            self.settings |= json.load(f)

    def get_settings(self, item):
        try:
            if self.settings:
                return self.settings[item]
        except KeyError:
            raise ConfigurationRequestError(item)
