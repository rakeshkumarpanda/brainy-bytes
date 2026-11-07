# 5.1 Exceptions: try, except, else, finally and raise
# Example "with" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

import os, tempfile
path = os.path.join(tempfile.gettempdir(), "demo_exceptions.txt")

f = open(path, "w")
try:
    f.write("first line\n")
    1 / 0                       # something goes wrong in the middle
except ZeroDivisionError:
    print("handled the error")
finally:
    f.close()                   # the file is closed whatever happened
print("closed:", f.closed)

with open(path, "w") as g:      # with does the same try and finally for you
    g.write("safe\n")
print("closed:", g.closed)
os.remove(path)
