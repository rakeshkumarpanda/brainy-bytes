# 6.1 Regular expressions
# Example "greedy" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

import re

html = "<b>bold</b> and <i>italic</i>"
print(re.findall(r"<.+>", html))              # greedy: as much as possible
print(re.findall(r"<.+?>", html))             # lazy: as little as possible
print(re.findall(r"\bcat\b", "cat concat cats cat."))   # \b is a word edge

# lookahead (?=...) and negative lookahead (?!...) check without using up characters
strong = re.compile(r"^(?=.*\d)(?=.*[a-z])(?=.*[A-Z]).{8,}$")
for pw in ["password", "Passw0rd", "Pa1"]:
    print(pw, bool(strong.match(pw)))

print(re.findall(r"(?<=\$)\d+", "cost $30, tax $4, 7 items"))   # lookbehind: digits after a $
print(re.findall(r"\b\d+\b(?! items)", "cost 30, 7 items"))
