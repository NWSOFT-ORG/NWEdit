from src.Components.search import re_search


def test_case():
    res_case = re_search("A", "Aa")
    res_nocase = re_search("A", "Aa", nocase=True)

    assert res_case
    assert res_nocase
    assert len(res_case) < len(res_nocase)


def test_full_word():
    res = re_search("a", "abc")
    res_word = re_search("a", "abc", full_word=True)
    assert not res_word  # Should be empty
    assert res


def test_re():
    res = re_search(r"\d\d", "12")
    res_re = re_search(r"\d\d", "12", regex=True)

    assert not res
    assert res_re


def test_case_word():
    res = re_search("a", "AA")
    res_case_word = re_search("a", "AA A", nocase=True, full_word=True)

    assert not res
    assert res_case_word


def test_case_re():
    res = re_search(r"(a|b)+", "AB", regex=True)
    res_case_re = re_search(r"(a|b)+", "AB", regex=True, nocase=True)
    
    assert not res
    assert res_case_re
