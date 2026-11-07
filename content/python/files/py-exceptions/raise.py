# 5.1 Exceptions: try, except, else, finally and raise
# Example "raise" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

def set_age(age):
    if not isinstance(age, int):
        raise TypeError("age must be a whole number")
    if age < 0 or age > 150:
        raise ValueError(f"age {age} is not possible")
    return age

for value in [30, -4, "ten"]:
    try:
        print("ok:", set_age(value))
    except (TypeError, ValueError) as err:
        print(type(err).__name__ + ":", err)

def load(text):
    try:
        return int(text)
    except ValueError as err:
        raise RuntimeError("could not load the settings") from err   # keep the cause

try:
    load("abc")
except RuntimeError as err:
    print(err, "| caused by:", repr(err.__cause__))
