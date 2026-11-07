# 2.2 Loops: while, for, range, break and continue
# Example "range" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

print(list(range(5)))           # [0, 1, 2, 3, 4]
print(list(range(2, 8)))        # start 2, stop 8 (not included)
print(list(range(1, 10, 3)))    # step 3
print(list(range(10, 0, -2)))   # counting down
print(list(range(5, 1)))        # empty: you cannot go up from 5 to 1
print(len(range(0, 100, 7)), range(0, 100, 7)[-1])
