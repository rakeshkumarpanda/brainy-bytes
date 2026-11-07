# 1.4 Input, output and formatting text
# Example "many" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>
# This program reads input. Type these lines when it asks:
#   78 91 64
#   12 30

# Several numbers typed on one line, separated by spaces
line = input("Enter three marks: ")
parts = line.split()             # ["78", "91", "64"]
a, b, c = int(parts[0]), int(parts[1]), int(parts[2])
print("Total:", a + b + c)
print("Average:", (a + b + c) / 3)

# The same in one line with map()
x, y = map(int, input("Enter two numbers: ").split())
print(x, "+", y, "=", x + y)
