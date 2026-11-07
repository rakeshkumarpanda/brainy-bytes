# 2.3 Context managers and the with statement
# Example "files" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

import os
import tempfile

path = os.path.join(tempfile.mkdtemp(), "notes.txt")

with open(path, "w") as f:                     # the file is closed when the block ends
    f.write("line one\n")
print("closed after with?", f.closed)

try:
    with open(path) as f:
        print(f.readline().strip())
        raise ValueError("something went wrong")
except ValueError as err:
    print("error:", err, "| closed anyway?", f.closed)

# what with saves you from writing by hand
f = open(path)
try:
    print(len(f.read()), "characters")
finally:
    f.close()
print(f.closed)
