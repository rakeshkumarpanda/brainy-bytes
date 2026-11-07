# 5.3 Files: reading, writing, modes, paths and streams
# Example "with" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

import os, tempfile
os.chdir(tempfile.mkdtemp())

with open("a.txt", "w") as f:
    f.write("hello")
    print("inside, closed?", f.closed)
print("after, closed?", f.closed)       # with closed it, even if an error had happened

with open("a.txt") as src, open("b.txt", "w") as dst:   # two files in one with
    dst.write(src.read().upper())
print(open("b.txt").read())
