# 2.2 Loops: while, for, range, break and continue
# Example "enumzip" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

names = ["Asha", "Ravi", "Meera"]
scores = [88, 72, 95]

for i, name in enumerate(names, start=1):     # position and value together
    print(i, name)

for name, score in zip(names, scores):        # walk two lists side by side
    print(name, "scored", score)

for name in reversed(names):
    print(name, end=" ")
print()
for name in sorted(names):
    print(name, end=" ")
print()
