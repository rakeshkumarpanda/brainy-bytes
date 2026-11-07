# 2.2 Loops: while, for, range, break and continue
# Example "patterns" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

marks = [72, 45, 91, 38, 66]

total = 0                       # accumulator
for m in marks:
    total += m
print("total", total)

passed = 0                      # counter
for m in marks:
    if m >= 40:
        passed += 1
print("passed", passed)

best = marks[0]                 # running maximum
for m in marks:
    if m > best:
        best = m
print("best", best)

first_fail = None               # search with break
for m in marks:
    if m < 40:
        first_fail = m
        break
print("first fail", first_fail)
