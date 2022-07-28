import keyword
import random
import sys

from src.Utils.functions import ILLEGAL_CHARS, ILLEGAL_NAMES, is_illegal_filename, is_valid_name, is_binary_string


def generate_words_with_spaces():
    first_word_len = random.randint(3, 10)
    second_word_len = random.randint(3, 10)
    first_word = "".join((chr(c) for c in range(65, 65 + first_word_len)))
    second_word = "".join((chr(c) for c in range(65, 65 + second_word_len)))
    return " ".join((first_word, second_word))


def test_is_illegal_filename():
    for name in ILLEGAL_NAMES + ILLEGAL_CHARS:
        assert is_illegal_filename(name)


def test_is_valid_name():
    for keyw in keyword.kwlist:
        assert not is_valid_name(keyw)
    assert generate_words_with_spaces()
    assert not is_valid_name(generate_words_with_spaces())


def test_is_binary_string():
    with open(sys.executable, "rb") as f:
        assert is_binary_string(f.read())  # Python should be binary
    with open(__file__, "rb") as f:
        assert not is_binary_string(f.read())  # This file should be UTF-8
