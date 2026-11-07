# 3.3 Tuples and sets: fixed records and unique items
# Example "unpack" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

def min_max(numbers):
    return min(numbers), max(numbers)     # returns one tuple

low, high = min_max([4, 9, 1, 7])         # unpack it into two names
print(low, high)

students = [("Asha", 88), ("Ravi", 72), ("Meera", 95)]
for name, score in students:              # unpack in the loop
    print(name, score)

best = max(students, key=lambda pair: pair[1])
print("best:", best)
print(sorted(students, key=lambda pair: pair[1], reverse=True))

a, b = 1, 2
a, b = b, a        # swap: the right side is packed into a tuple first
print(a, b)
