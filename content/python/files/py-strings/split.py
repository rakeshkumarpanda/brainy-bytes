# 3.1 Strings: text, slicing, methods and Unicode
# Example "split" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

line = "apple,mango,,banana"
parts = line.split(",")
print(parts, len(parts))
print("  many   spaces here ".split())      # no argument: split on any run of spaces
print("a-b-c-d".split("-", 2))             # at most 2 splits
print("a-b-c-d".rsplit("-", 1))
print("-".join(["2026", "11", "07"]))
print("".join(reversed("stressed")))
print("user@example.com".partition("@"))
print("one\ntwo\nthree".splitlines())
