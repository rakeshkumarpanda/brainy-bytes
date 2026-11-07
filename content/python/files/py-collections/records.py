# 4.2 collections, heapq and bisect
# Example "records" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

from collections import ChainMap, OrderedDict, defaultdict, namedtuple

Point = namedtuple("Point", ["x", "y"])
p = Point(3, 4)
print(p, p.x, p[1])
x, y = p                                       # still a tuple: unpacking and indexing work
print(p._replace(x=10), p._asdict(), Point._fields)

cache = OrderedDict()
for key in ["a", "b", "c"]:
    cache[key] = key.upper()
cache.move_to_end("a")                         # "a" was just used: make it the newest
print(list(cache))
print(cache.popitem(last=False))               # remove the oldest: the heart of an LRU cache

defaults = {"theme": "light", "lang": "en", "size": 12}
user = {"theme": "dark"}
settings = ChainMap(user, defaults)            # look in user first, then in defaults
print(settings["theme"], settings["lang"], len(settings))


def tree():
    return defaultdict(tree)                   # a dict that makes nested dicts when needed


menu = tree()
menu["drinks"]["hot"]["tea"] = 2
print(menu["drinks"]["hot"]["tea"], list(menu["drinks"]))
