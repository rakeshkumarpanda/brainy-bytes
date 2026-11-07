# 3.3 Tuples and sets: fixed records and unique items
# Example "tuple" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

point = (3, 7)
colours = ("red", "green", "blue")
one = (5,)            # a tuple with one item needs the comma
not_tuple = (5)       # just the number 5 in brackets
empty = ()
packed = 1, 2, 3      # brackets are optional: the commas make the tuple
print(point, colours, one, not_tuple, empty, packed)
print(type(one), type(not_tuple))
print(colours[0], colours[-1], colours[1:])
print(len(colours), "green" in colours, colours.index("blue"), (1, 2, 1).count(1))
print((1, 2) + (3,), (0,) * 4)
