import re

BRAKETED = re.compile(r'\[(.*)]')


def is_braketed(string):
    """Check if a string is braketed"""
    return BRAKETED.match(string) is not None


def find_braketed_text(text, string):
    """Find specified braketed text in a string"""
    pattern = re.compile(fr'\[{text}]')
    return list(re.finditer(pattern, string))


def replace_braketed(string, item, replace):
    """Replace braketed text in a string"""
    for text in find_braketed_text(item, string):
        string = string.replace(text.group(0), replace)

    return string
