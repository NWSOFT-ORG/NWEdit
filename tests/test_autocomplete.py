import pprint

from src.Components.autocomplete import sep_words

STRING = """\
Here is some text, here is some other text.
Here is some text, here is some other text.
Here is some text, here is some other text.

\\abc/def*ghi&jkl^mno(p)qr%s$t#u@v!`w~x-y+z
1[2]3:4;5'6\"7_8|9<1>0?11"""


def test_sep_words():
    words = sep_words(STRING)
    print()
    pprint.pprint(words)
    assert words
    assert len(words) > 1

    for word in words:
        assert words.count(word) == 1

    assert STRING.count(words[0]) > STRING.count(words[-1])
