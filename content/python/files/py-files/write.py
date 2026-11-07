# 5.3 Files: reading, writing, modes, paths and streams
# Example "write" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

import os, tempfile
os.chdir(tempfile.mkdtemp())          # work in an empty folder made for this demo

f = open("shopping.txt", "w", encoding="utf-8")
f.write("milk\n")                      # write() does not add a new line by itself
f.write("eggs\n")
f.writelines(["rice\n", "tea\n"])      # nor does writelines()
print("bread", file=f)                 # print() adds the new line
f.close()

print(open("shopping.txt", encoding="utf-8").read())
print(os.path.getsize("shopping.txt"), "bytes")
