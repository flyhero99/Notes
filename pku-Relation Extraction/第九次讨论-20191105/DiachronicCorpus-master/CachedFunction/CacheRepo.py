from abc import ABC, abstractmethod


class CacheRepo(ABC):
    @abstractmethod
    def get(self, key):
        pass

    @abstractmethod
    def save(self, key, content):
        pass

    @abstractmethod
    def has_key(self, key):
        pass

    def __getitem__(self, item):
        return self.get(item)

    def __setitem__(self, key, value):
        return self.save(key, value)

    def __contains__(self, item):
        return self.has_key(item)
