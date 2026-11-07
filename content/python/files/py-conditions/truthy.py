# 2.1 Making decisions: if, elif, else and match
# Example "truthy" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

values = [0, 1, -2, 0.0, "", "0", " ", [], [0], {}, None, True, False]
for v in values:
    if v:
        print(repr(v).ljust(6), "is truthy")
    else:
        print(repr(v).ljust(6), "is falsy")
