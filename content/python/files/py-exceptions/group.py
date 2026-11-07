# 5.1 Exceptions: try, except, else, finally and raise
# Example "group" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

errors = ExceptionGroup("two checks failed", [ValueError("bad age"), KeyError("name")])

try:
    raise errors
except* ValueError as group:       # except* (Python 3.11+) handles part of a group
    print("value problems:", [str(e) for e in group.exceptions])
except* KeyError as group:
    print("missing keys:", [str(e) for e in group.exceptions])
