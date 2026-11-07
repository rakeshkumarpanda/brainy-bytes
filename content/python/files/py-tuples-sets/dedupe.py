# 3.3 Tuples and sets: fixed records and unique items
# Example "dedupe" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

orders = ["tea", "coffee", "tea", "juice", "coffee", "tea"]

print(len(set(orders)), "different drinks")
print(sorted(set(orders)))

# set() loses the order. dict.fromkeys keeps the first time each item appears
print(list(dict.fromkeys(orders)))

# The same with a loop and a set of seen items
unique = []
seen = set()
for item in orders:
    if item not in seen:
        seen.add(item)
        unique.append(item)
print(unique)
