from copy import deepcopy

from CachedFunction.CacheRepo import CacheRepo


class MemRepo(CacheRepo):
    def __init__(self):
        self.storage = {}

    def get(self, key):
        return deepcopy(self.storage.get(key, None))

    def save(self, key, content):
        self.storage[key] = deepcopy(content)
        return True

    def has_key(self, key):
        return key in self.storage
