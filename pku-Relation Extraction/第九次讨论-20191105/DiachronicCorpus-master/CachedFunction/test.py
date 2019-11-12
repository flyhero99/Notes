from CachedFunction.CacheRepo import CacheRepo
from CachedFunction.CacheManager import CacheManager
from CachedFunction.MemRepo import MemRepo

cm = CacheManager()


@cm.register
def add(a, b, c):
    print('func called')
    return a+b+c


if __name__ == '__main__':
    mr = MemRepo()
    mr.save('a', 123)
    mr['b'] = 321
    print(mr.get('a'))
    print('b' in mr)
    print(mr['b'])

    print(cm.add_repo(mr))

    print(add(1, 2, 3))
    print(add(1, 2, 3))
    print(add(1, 2, 3, force_refresh=True))
