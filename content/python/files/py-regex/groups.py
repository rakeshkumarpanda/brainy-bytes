# 6.1 Regular expressions
# Example "groups" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

import re

m = re.search(r"(\d{4})-(\d{2})-(\d{2})", "Due: 2026-11-07.")
print(m.group(0), m.group(1), m.groups())

m = re.search(r"(?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2})", "Due: 2026-11-07.")
print(m["year"], m.groupdict())

print(re.findall(r"(\w+)@(\w+)\.com", "ann@mail.com, bo@shop.com"))   # groups: findall returns tuples
print(re.findall(r"(?:ha)+", "hahaha hoho haha"))                     # (?:...) groups without capturing
print(re.search(r"\b(\w+) \1\b", "this is is a typo").group())        # \1 means the same text again
print(re.findall(r"cat|dog", "cat, dog, bird, dogs"))                 # | means or
