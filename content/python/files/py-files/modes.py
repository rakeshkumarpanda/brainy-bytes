# 5.3 Files: reading, writing, modes, paths and streams
# Example "modes" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

import os, tempfile
os.chdir(tempfile.mkdtemp())

with open("log.txt", "w") as f:      # w: create or empty
    f.write("start\n")
with open("log.txt", "a") as f:      # a: add to the end
    f.write("more\n")
print(open("log.txt").read().splitlines())

with open("log.txt", "w") as f:      # w again: the old text is gone
    f.write("fresh\n")
print(open("log.txt").read().splitlines())

try:
    open("log.txt", "x")             # x: create, but only if it does not exist
except FileExistsError as err:
    print("FileExistsError:", err.strerror)

with open("log.txt", "r+") as f:     # r+: read and write, no emptying
    f.write("FR")                    # overwrites the first two characters
print(open("log.txt").read().splitlines())
