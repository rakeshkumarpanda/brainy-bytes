# 2.1 Making decisions: if, elif, else and match
# Example "walrus" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

data = [3, 8, 12, 5]
if (n := len(data)) > 3:                    # assign and test in one go
    print("Too many items:", n)

words = ["apple", "fig", "banana", "kiwi"]
long_words = [w.upper() for w in words if (size := len(w)) > 4]
print(long_words, "last size checked:", size)
