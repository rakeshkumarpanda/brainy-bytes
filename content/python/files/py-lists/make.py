# 3.2 Lists: storing, changing, sorting and copying
# Example "make" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

marks = [72, 45, 91, 38]
mixed = ["Asha", 21, 5.8, True]     # a list can hold any types
empty = []
letters = list("abc")               # list() turns any iterable into a list
numbers = list(range(1, 6))
print(marks, mixed, empty, letters, numbers)
print(len(marks), marks[0], marks[-1], marks[1:3])
print(91 in marks, 50 not in marks)
print(min(marks), max(marks), sum(marks), sum(marks) / len(marks))
