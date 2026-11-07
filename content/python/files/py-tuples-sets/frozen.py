# 3.3 Tuples and sets: fixed records and unique items
# Example "frozen" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

vowels = frozenset("aeiou")
print(vowels, "e" in vowels)
try:
    vowels.add("y")
except AttributeError as err:
    print("AttributeError:", err)

groups = {frozenset({"a", "b"}), frozenset({"b", "a"})}   # equal sets, so one item
print(len(groups))
squares = {n * n for n in range(-3, 4)}                   # a set comprehension
print(sorted(squares))
