# 3.1 Strings: text, slicing, methods and Unicode
# Example "ops" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

print("ab" + "cd")        # join two strings
print("ha" * 3)           # repeat
print("cat" in "concatenate", "dog" not in "hotdog")
print("apple" < "banana", "Zebra" < "apple", "10" < "9")
print(min("python"), max("python"))
for ch in "abc":
    print(ch, ord(ch))
print(chr(65), chr(97), chr(8377))
