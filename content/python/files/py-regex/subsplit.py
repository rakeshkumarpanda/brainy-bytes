# 6.1 Regular expressions
# Example "subsplit" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

import re

print(re.sub(r"\s+", " ", "too    many   spaces"))
print(re.sub(r"(\d{4})-(\d{2})-(\d{2})", r"\3/\2/\1", "2026-11-07"))   # reorder with groups
print(re.sub(r"\d+", lambda m: str(int(m.group()) * 2), "3 apples and 10 pears"))
print(re.subn(r"o", "0", "foo boo"))                                  # (new text, how many)
print(re.split(r"[,;\s]+", "a, b;c  d"))
print(re.findall(r"^\w+", "one\ntwo\nthree", flags=re.MULTILINE))     # ^ at the start of every line
print(re.findall(r"python", "Python PYTHON python", flags=re.IGNORECASE))

price = re.compile(r"""
    \$                # a dollar sign
    (\d+)             # dollars
    (?:\.(\d{2}))?    # optional cents
""", re.VERBOSE)
print(price.findall("Tea $3.50, cake $4, coffee $12.05"))
print(re.escape("1+1=2?"))
