# 3.4 Dictionaries: keys, values and hash tables
# Example "keys" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

d = {}
d[1] = "int one"
d[1.0] = "float one"     # 1 == 1.0 and hash(1) == hash(1.0): the same key
d[True] = "true"         # True == 1 too
print(d)
print({(1, 2): "tuple key ok"})
try:
    d[[1, 2]] = "list"
except TypeError as err:
    print("TypeError:", err)
print(hash("hi") == hash("hi"), hash(10), hash(-1))
