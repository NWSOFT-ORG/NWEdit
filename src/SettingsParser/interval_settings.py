from src.modules import EditorErr, json


class IntervalSettings:
    def __init__(self):
        with open("Config/interval.json") as f:
            self.settings = json.load(f)

    def get_settings(self, item):
        try:
            return self.settings[item]
        except KeyError:
            raise EditorErr(f"Wrong request item: {item}")
