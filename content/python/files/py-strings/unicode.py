# 3.1 Strings: text, slicing, methods and Unicode
# Example "unicode" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

for ch in ["A", "a", "é", "₹", "न", "😀"]:
    data = ch.encode("utf-8")
    print(ch, "code point", ord(ch), "hex", hex(ord(ch)), "bytes", len(data), list(data))

word = "café"
print(len(word), len(word.encode("utf-8")))
raw = word.encode("utf-8")
print(raw, raw.decode("utf-8"))
print("Straße".lower(), "Straße".casefold())   # casefold is the stronger lower case for comparing
