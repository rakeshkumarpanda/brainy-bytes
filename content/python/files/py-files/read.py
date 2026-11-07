# 5.3 Files: reading, writing, modes, paths and streams
# Example "read" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

import os, tempfile
os.chdir(tempfile.mkdtemp())
with open("marks.txt", "w", encoding="utf-8") as f:
    f.write("Asha 88\nRavi 72\nMeera 95\n")

with open("marks.txt", encoding="utf-8") as f:   # "r" (read text) is the default mode
    print(repr(f.read()))                         # everything as one string

with open("marks.txt", encoding="utf-8") as f:
    print(repr(f.readline()))                     # one line, with its new line
    print(f.readlines())                          # the remaining lines as a list

total = 0
with open("marks.txt", encoding="utf-8") as f:
    for line in f:                                # best: one line at a time
        name, mark = line.split()
        total += int(mark)
print("total", total)
