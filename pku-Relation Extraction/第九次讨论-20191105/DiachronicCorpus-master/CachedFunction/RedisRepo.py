import redis
import pandas as pd
from pandas import DataFrame
import pickle

from CachedFunction.CacheRepo import CacheRepo


class RedisRepo(CacheRepo):
    def __init__(self, host='localhost', port=6379, db=0):
        self.redis = redis.Redis(host, port, db)

    def get(self, key):
        value = self.redis.get(key)
        if value is None:
            return None
        if b'DataFrame' in value and b'block_manager' in value:
            return pd.read_msgpack(value)
        return pickle.loads(value)

    def save(self, key, content):
        if isinstance(content, DataFrame):
            self.redis.set(key, content.to_msgpack(compress='zlib'))
        else:
            self.redis.set(key, pickle.dumps(content))
        return True

    def has_key(self, key):
        return self.redis.exists(key)
