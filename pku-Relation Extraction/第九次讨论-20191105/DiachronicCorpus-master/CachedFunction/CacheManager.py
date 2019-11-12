import json
import logging
import uuid
from collections import OrderedDict
from functools import wraps

from CachedFunction.CacheRepo import CacheRepo
from CachedFunction.NotInCacheError import NotInCacheError


class CacheManager:
    def __init__(self):
        self.__repos = OrderedDict()

    def add_repo(self, repo, name=None):
        if not isinstance(repo, CacheRepo):
            raise TypeError('Need an instance of CacheRepo.')
        if name is None:
            name = uuid.uuid4()
        if name in self.__repos:
            raise ValueError('Duplicate repo name %s.', name)
        self.__repos[name] = repo
        return name

    def get(self, key):
        if len(self.__repos) == 0:
            logging.warning('No repo in CacheManager')
        for name, repo in self.__repos.items():
            if key in repo:
                return repo[key]
        raise NotInCacheError(key)

    def register(self, func):
        def gen_key(*args, **kwargs):
            part1 = json.dumps(args)
            part2 = json.dumps(kwargs)
            return '|'.join([func.__name__, part1, part2])

        @wraps(func)
        def wrapper(*args, **kwargs):
            force_refresh = kwargs.get('force_refresh', False)
            if 'force_refresh' in kwargs:
                del kwargs['force_refresh']
            key = gen_key(*args, **kwargs)
            if force_refresh:
                value = func(*args, **kwargs)
            else:
                try:
                    value = self.get(key)
                except NotInCacheError:
                    value = func(*args, **kwargs)
            if len(self.__repos) > 0:
                name = next(iter(self.__repos.keys()))
                self.__repos[name][key] = value
            return value
        return wrapper
