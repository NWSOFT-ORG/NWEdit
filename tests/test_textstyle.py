from src.Dialog.textstyle import listfonts


def test_listfonts():
    fonts = listfonts()
    assert len(fonts)
