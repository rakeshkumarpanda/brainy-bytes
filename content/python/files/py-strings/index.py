# 3.1 Strings: text, slicing, methods and Unicode
# Example "index" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

word = "PYTHON"
print(word[0], word[1], word[5])     # first, second, last
print(word[-1], word[-2])            # negative index counts from the right
print(word[0:2], word[2:], word[:3]) # slices: start included, stop excluded
print(word[::2], word[::-1])         # every second letter, and reversed
print(word[1:100])                   # a slice never fails
try:
    print(word[10])
except IndexError as err:
    print("IndexError:", err)
