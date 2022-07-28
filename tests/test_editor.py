from src.editor import Tabs


var = 0


def trigger(_):
    global var
    var += 1


def test_tabs():
    global var
    tabs = Tabs()
    tabs.set_triggger(trigger)

    tabs["a"] = "a"  # Trigger a change
    tabs["a"] = "b"
    tabs["b"] = "c"
    tabs.pop("b")

    assert var
    assert var == 5
