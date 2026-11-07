# 5.3 Files: reading, writing, modes, paths and streams
# Example "encoding" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

import os, tempfile
os.chdir(tempfile.mkdtemp())

with open("greet.txt", "w", encoding="utf-8") as f:
    f.write("नमस्ते ₹100 café\n")
print(os.path.getsize("greet.txt"), "bytes for", len("नमस्ते ₹100 café\n"), "characters")

print(open("greet.txt", encoding="utf-8").read().strip())
try:
    open("greet.txt", encoding="ascii").read()
except UnicodeDecodeError as err:
    print("UnicodeDecodeError:", err.reason)
print(open("greet.txt", encoding="ascii", errors="replace").read().strip()[:12])
