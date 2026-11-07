# 4.1 Functions: def, return and every kind of argument
# Example "ret" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

def show_double(x):
    print(x * 2)          # prints, returns nothing

def double(x):
    return x * 2          # returns, prints nothing

a = show_double(5)
b = double(5)
print("a is", a, "and b is", b)

def grade(mark):
    if mark >= 90:
        return "A"        # return also leaves the function at once
    if mark >= 75:
        return "B"
    return "C"

print(grade(95), grade(80), grade(40))

def min_max(items):
    return min(items), max(items)     # one tuple, two values

low, high = min_max([7, 2, 9])
print(low, high)
