# 3.4 Dictionaries: keys, values and hash tables
# Example "views" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

d = {"a": 1, "b": 2}
keys = d.keys()          # a live view, not a copy
d["c"] = 3
print(keys)              # the view sees the new key
print(keys & {"a", "z"}) # key views work like sets

try:
    for k in d:
        d["new_" + k] = 0    # changing the size while looping
except RuntimeError as err:
    print("RuntimeError:", err)

d = {"a": 1, "b": 2}
for k in list(d):            # loop over a copy of the keys instead
    d["new_" + k] = 0
print(d)
