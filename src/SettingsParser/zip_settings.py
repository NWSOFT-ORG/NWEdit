import os
import zipfile
from pathlib import Path

from src.Components.commondialog import ErrorInfoDialog
from src.Components.filedialog import DirectoryOpenDialog, FileOpenDialog
from src.constants import APPDIR


class ZipSettings:
    def __init__(self, master):
        self.master = master

    @staticmethod
    def __zip_settings(backupdir):
        def zipdir(path, zip_obj):
            for root, _, files in os.walk(path):
                for file in files:
                    zip_obj.write(
                        os.path.join(root, file),
                        os.path.relpath(os.path.join(root, file), Path(path).parent),
                    )

        with zipfile.ZipFile(
                os.path.join(backupdir, "Config.zip"), "w", zipfile.ZIP_DEFLATED
        ) as zipobj:
            zipdir("Config/", zipobj)
        ErrorInfoDialog(text="Settings backed up.", title="Done")

    def zipsettings(self):
        DirectoryOpenDialog(self.master, self.__zip_settings)

    @staticmethod
    def __unzip_settings(backupdir):
        try:
            with zipfile.ZipFile(backupdir) as zipobj:
                zipobj.extractall(path=APPDIR)
            ErrorInfoDialog(text="Settings extracted. Please restart to apply changes.", title="Done")
        except (zipfile.BadZipFile, zipfile.BadZipfile, zipfile.LargeZipFile):
            pass

    def unzipsettings(self):
        FileOpenDialog(Path("~").expanduser(), self.master, self.__unzip_settings)
