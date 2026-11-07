# 4.3 lambda, map, filter and comprehensions
# Example "key" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

students = [("Asha", 88), ("Ravi", 72), ("Meera", 95), ("John", 72)]

print(sorted(students, key=lambda s: s[1]))                 # by mark
print(sorted(students, key=lambda s: s[1], reverse=True))   # highest first
print(sorted(students, key=lambda s: (-s[1], s[0])))        # mark down, then name up
print(max(students, key=lambda s: s[1]))
print(min(["kiwi", "fig", "banana"], key=len))

from operator import itemgetter
print(sorted(students, key=itemgetter(1, 0)))               # the same as lambda s: (s[1], s[0])
