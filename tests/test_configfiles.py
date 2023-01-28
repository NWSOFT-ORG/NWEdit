from pathlib import Path

from src.constants import WINDOWS
from src.SettingsParser.configfiles import ALL, config_dir_from_name, to_platform_specific_path


def test_configfiles():
    all_exsists = True
    for path in ALL:
        print(path, end=" ")

        # Test for existence of all paths
        all_exsists &= path.exists()
        print(f"Path exists: {path.exists()}", end=" ")

        print(f"Path is file: {path.is_file()}", end=" ")
        print()

    assert all_exsists


def test_to_platform_specific_path():
    # Test for correct conversion of paths
    if WINDOWS:
        assert to_platform_specific_path(Path("C:/Users")) == Path("C:\\Users")
        assert to_platform_specific_path("C:/Users") == "C:\\Users"

        assert to_platform_specific_path(Path("C:\\Users")) == Path("C:\\Users")
        assert to_platform_specific_path("C:\\Users") == "C:\\Users"

        assert to_platform_specific_path(Path("C:/Users")) == Path("C:\\Users")
        assert to_platform_specific_path("C:/Users") == "C:\\Users"

        assert to_platform_specific_path(Path("C:\\Users")) == Path("C:\\Users")
        assert to_platform_specific_path("C:\\Users") == "C:\\Users"

        assert to_platform_specific_path(Path("C:/Users")) == Path("C:\\Users")
        assert to_platform_specific_path("C:/Users") == "C:\\Users"

        assert to_platform_specific_path(Path("C:\\Users")) == Path("C:\\Users")
        assert to_platform_specific_path("C:\\Users") == "C:\\Users"

        assert to_platform_specific_path(Path("C:/Users")) == Path("C:\\Users")
        assert to_platform_specific_path("C:/Users") == "C:\\Users"
    else:
        assert to_platform_specific_path(Path("C:/Users")) == Path("C:/Users")
        assert to_platform_specific_path("C:/Users") == "C:/Users"

        assert to_platform_specific_path(Path("C:\\Users")) == Path("C:/Users")
        assert to_platform_specific_path("C:\\Users") == "C:/Users"

        assert to_platform_specific_path(Path("C:/Users")) == Path("C:/Users")
        assert to_platform_specific_path("C:/Users") == "C:/Users"

        assert to_platform_specific_path(Path("C:\\Users")) == Path("C:/Users")
        assert to_platform_specific_path("C:\\Users") == "C:/Users"

        assert to_platform_specific_path(Path("C:/Users")) == Path("C:/Users")
        assert to_platform_specific_path("C:/Users") == "C:/Users"

        assert to_platform_specific_path(Path("C:\\Users")) == Path("C:/Users")
        assert to_platform_specific_path("C:\\Users") == "C:/Users"

        assert to_platform_specific_path(Path("C:/Users")) == Path("C:/Users")
        assert to_platform_specific_path("C:/Users") == "C:/Users"


def test_project_path_from_name():
    if WINDOWS:
        assert config_dir_from_name("C:\\Project\\A") == "C:\\Project\\A\\.NWEdit"
        assert config_dir_from_name(Path("C:\\Project\\A")) == Path("C:\\Project\\A\\.NWEdit")
    else:
        assert config_dir_from_name("/Project/A") == "/Project/A/.NWEdit"
        assert config_dir_from_name(Path("/Project/A")) == Path("/Project/A/.NWEdit")
