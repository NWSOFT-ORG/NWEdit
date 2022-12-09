import time
from functools import wraps

from src.constants import logger


def timeit(function):
    """Measures the time of a function
    Use as a decorator:

    @timeit
    def function():
        ...
    """

    @wraps(function)
    def time_function(*args, **kwargs):
        start = time.time()
        res = function(*args, **kwargs)
        end = time.time()

        elapsed = end - start
        logger.debug(f"{function.__name__} taken {elapsed} seconds.")
        return res

    return time_function
