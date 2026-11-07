# 4.1 Functions: def, return and every kind of argument
# Example "unpackcall" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

def move(x, y, speed):
    print(f"to ({x}, {y}) at {speed} km/h")

point = [3, 7]
move(*point, 40)                  # * spreads a list into positional arguments

settings = {"speed": 60, "y": 2, "x": 1}
move(**settings)                  # ** spreads a dict into keyword arguments

numbers = [4, 9, 1]
print(max(*numbers), max(numbers))
print(*numbers, sep=" | ")
