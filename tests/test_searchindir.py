import pprint

from src.Components.searchindir import list_all


def test_list_all():
    files = list_all("../tests/test_dir")
    pprint.pprint(files)

    assert files
