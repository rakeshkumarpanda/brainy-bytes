# 1.2 Variables, values, types and numeral systems
# Example "types" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

values = [42, 3.14, 2 + 3j, "Asha", True, None, 1_000_000, 0b1010, 0o17, 0xFF, 1.5e3]
for v in values:
    print(repr(v).ljust(12), type(v).__name__)
