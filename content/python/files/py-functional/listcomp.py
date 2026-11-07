# 4.3 lambda, map, filter and comprehensions
# Example "listcomp" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

nums = [3, 8, 1, 6, 5]

squares = [n * n for n in nums]
evens = [n for n in nums if n % 2 == 0]
labels = ["even" if n % 2 == 0 else "odd" for n in nums]   # if-else goes BEFORE for
print(squares)
print(evens)
print(labels)

words = ["  Apple ", "banana", " Cherry"]
clean = [w.strip().lower() for w in words]
print(clean)
print([len(w) for w in clean if w.startswith(("a", "c"))])
