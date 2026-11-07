# 6.1 Regular expressions
# Example "basics" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

import re

text = "Call 555-1234 or 555-9876 before 6 pm."

m = re.search(r"\d{3}-\d{4}", text)          # the first match anywhere
print(m.group(), m.start(), m.end(), m.span())
print(re.match(r"\d", text))                  # match only looks at the very start
print(re.fullmatch(r"\d{3}-\d{4}", "555-1234") is not None)   # the WHOLE string must match
print(re.findall(r"\d{3}-\d{4}", text))       # every match, as strings
for m in re.finditer(r"\d+", text):           # every match, as match objects
    print(m.group(), m.span())
print(len("\n"), len(r"\n"))                  # a raw string keeps the backslash
