from src.Components.commondialog import ErrorInfoDialog
from src.constants import logger
from src.SettingsParser.in_project_config import RunConfig


class Runner:
    def __init__(self, project):
        self.settings = RunConfig(project)

        self.project = project
        self.configuration = list(self.settings.configurations)[0]

    def set_configuration(self, configuration):
        self.configuration = configuration

    def run(self) -> None:
        """Runs the project"""

        # noinspection PyBroadException
        try:
            self.settings.run(self.configuration)
        except Exception:
            logger.exception(f"Cannot run configuration {self.configuration}:")
            ErrorInfoDialog(None, f"Cannot run this configuration: {self.configuration}")
