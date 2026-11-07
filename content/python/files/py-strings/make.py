# 3.1 Strings: text, slicing, methods and Unicode
# Example "make" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

a = 'single quotes'
b = "double quotes"
c = "It's easy"            # an apostrophe inside double quotes
d = 'She said "hi"'        # double quotes inside single quotes
e = """Three quotes
let a string run over
many lines"""
print(a, b, c, d, sep=" | ")
print(e)
print(len("hello"), len(""), len("  "))
print(str(42) + "!", str(3.5), str(True))
