# 3.4 Dictionaries: keys, values and hash tables
# Example "merge" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

base = {"theme": "light", "size": 12}
user = {"size": 14, "lang": "hi"}

print(base | user)              # new dict, the right side wins (Python 3.9+)
merged = {**base, **user}       # the older way
print(merged)
base |= user                    # update in place
print(base)

squares = {n: n * n for n in range(1, 6)}       # dict comprehension
print(squares)
flipped = {v: k for k, v in squares.items()}
print(flipped)
print(dict.fromkeys(["a", "b"], 0))
print(dict(zip(["x", "y"], [10, 20])))
