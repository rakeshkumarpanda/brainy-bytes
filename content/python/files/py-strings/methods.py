# 3.1 Strings: text, slicing, methods and Unicode
# Example "methods" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

s = "  Hello, World  "
print(repr(s.strip()), repr(s.lstrip()), repr(s.rstrip()))
t = s.strip()
print(t.upper(), t.lower(), t.swapcase())
print("hello world".title(), "hello world".capitalize())
print(t.replace("World", "Python"))
print(t.startswith("Hell"), t.endswith("!"))
print(t.find("o"), t.rfind("o"), t.find("z"), t.count("l"))
print(t.index("W"))
print("42".isdigit(), "abc".isalpha(), "a1".isalnum(), "   ".isspace())
print("7".zfill(3), "hi".center(8, "*"), "hi".ljust(5) + "|", "hi".rjust(5))
print("report.pdf".removesuffix(".pdf"), "Mr Rao".removeprefix("Mr "))
