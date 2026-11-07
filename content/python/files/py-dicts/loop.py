# 3.4 Dictionaries: keys, values and hash tables
# Example "loop" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

marks = {"Asha": 88, "Ravi": 72, "Meera": 95}

for name in marks:                 # looping gives the keys
    print(name, end=" ")
print()
for score in marks.values():
    print(score, end=" ")
print()
for name, score in marks.items():  # key and value together
    print(f"{name}: {score}")

print(list(marks.keys()), list(marks.values()))
print(max(marks, key=marks.get))   # the key with the largest value
print(sorted(marks.items(), key=lambda pair: pair[1], reverse=True))
