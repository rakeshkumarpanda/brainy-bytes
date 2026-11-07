# 3.3 Tuples and sets: fixed records and unique items
# Example "tupkey" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

# Tuples can be dict keys and set items, lists cannot
distance = {("Delhi", "Agra"): 233, ("Mumbai", "Pune"): 149}
print(distance[("Delhi", "Agra")])

seen = {(0, 0), (1, 2)}
print((1, 2) in seen)

try:
    bad = {[1, 2]: "x"}
except TypeError as err:
    print("TypeError:", err)

print(hash((1, 2)) == hash((1, 2)))
