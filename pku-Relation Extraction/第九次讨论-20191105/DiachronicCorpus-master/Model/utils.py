from functools import wraps

import time


def logger(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        st = time.time()
        result = fn(*args, **kwargs)
        et = time.time()
        print('{}({}, {}) takes {:.4f}ms'.format(fn.__name__, args, kwargs, (et - st) * 1000))
        return result
    return wrapper
