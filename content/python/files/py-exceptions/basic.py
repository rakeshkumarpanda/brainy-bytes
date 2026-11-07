# 5.1 Exceptions: try, except, else, finally and raise
# Example "basic" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

answers = ["42", "seven", "3.5", " 18 "]

for text in answers:
    try:
        age = int(text)               # may raise ValueError
        print("age is", age)
    except ValueError:
        print(repr(text), "is not a whole number")
print("the program keeps running")
