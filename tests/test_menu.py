from src.SettingsParser.menu import compare_platforms


def test_compare_platforms():
    assert compare_platforms("win32", "W")
    assert compare_platforms("darwin", "!W")
    assert compare_platforms("linux", "!W")

    assert compare_platforms("win32", "!M")
    assert compare_platforms("darwin", "M")
    assert compare_platforms("linux", "!M")

    assert compare_platforms("win32", "!L")
    assert compare_platforms("darwin", "!L")
    assert compare_platforms("linux", "L")
