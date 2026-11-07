# 4.1 Functions: def, return and every kind of argument
# Example "basic" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

def greet(name):              # name is a parameter
    print("Hello,", name)

greet("Asha")                 # "Asha" is an argument
greet("Ravi")

def area(width, height):
    return width * height     # send a value back to the caller

room = area(4, 5)
print("room:", room, "m2")
print("two rooms:", area(4, 5) + area(3, 3), "m2")
