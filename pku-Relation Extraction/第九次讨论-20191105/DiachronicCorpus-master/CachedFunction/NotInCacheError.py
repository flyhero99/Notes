class NotInCacheError(Exception):
    def __init__(self, key):
        err = '{} is not in cache manager.'.format(key)
        Exception.__init__(self, err)
