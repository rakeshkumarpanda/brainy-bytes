# 5.3 Files: reading, writing, modes, paths and streams
# Example "binary" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

import os, tempfile
os.chdir(tempfile.mkdtemp())

data = bytes([137, 80, 78, 71, 13, 10, 26, 10])   # the first 8 bytes of every PNG image
with open("fake.png", "wb") as f:                 # b: binary, no encoding, no new line changes
    f.write(data)

with open("fake.png", "rb") as f:
    head = f.read(4)
print(head, list(head), head[1:4].decode("ascii"))

buffer = bytearray(8)                             # a changeable block of bytes
with open("fake.png", "rb") as f:
    count = f.readinto(buffer)                    # fill it straight from the file
print(count, buffer[:4])

with open("fake.png", "rb") as f:
    f.seek(4)                                     # jump to byte 4
    print(f.tell(), f.read(2))
