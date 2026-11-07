# 4.3 lambda, map, filter and comprehensions
# Example "dictset" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

words = ["apple", "fig", "banana", "kiwi", "fig"]

lengths = {w: len(w) for w in words}             # dict comprehension
print(lengths)
first_letters = {w[0] for w in words}            # set comprehension
print(sorted(first_letters))
long_words = {w: n for w, n in lengths.items() if n > 3}
print(long_words)
flipped = {n: w for w, n in lengths.items()}     # later words win for equal lengths
print(flipped)
