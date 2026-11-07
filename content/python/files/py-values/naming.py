# 1.2 Variables, values, types and numeral systems
# Example "naming" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

import keyword
names = ["total", "total_price", "_hidden", "price2", "2price", "class", "Total", "my-name", "año"]
for name in names:
    ok = name.isidentifier() and not keyword.iskeyword(name)
    print(name.ljust(12), "valid" if ok else "NOT valid")
