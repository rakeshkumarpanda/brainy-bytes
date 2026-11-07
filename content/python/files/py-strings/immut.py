# 3.1 Strings: text, slicing, methods and Unicode
# Example "immut" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

name = "rita"
try:
    name[0] = "R"
except TypeError as err:
    print("TypeError:", err)

# You cannot change a string, but you can build a new one
name = "R" + name[1:]
print(name)
print(name.upper(), name)     # upper() returns a new string, name is unchanged
