# 3.4 Dictionaries: keys, values and hash tables
# Example "internals" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

import sys
d = {}
last = sys.getsizeof(d)
print("empty dict:", last, "bytes")
for i in range(25):
    d[i] = i
    size = sys.getsizeof(d)
    if size != last:
        print("adding key number", len(d), "grew the dict to", size, "bytes")
        last = size
