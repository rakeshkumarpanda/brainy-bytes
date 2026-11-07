# 5.3 Files: reading, writing, modes, paths and streams
# Example "osmod" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

import os, shutil, tempfile
os.chdir(tempfile.mkdtemp())

os.makedirs("photos/2026/trip", exist_ok=True)
for name in ["a.jpg", "b.jpg", "c.txt"]:
    open(os.path.join("photos", "2026", "trip", name), "w").close()

print(sorted(os.listdir("photos/2026/trip")))
for folder, subfolders, names in os.walk("photos"):
    print(folder.replace(os.sep, "/"), subfolders, sorted(names))

os.remove("photos/2026/trip/c.txt")
os.rename("photos/2026/trip/a.jpg", "photos/2026/trip/beach.jpg")
print(sorted(os.listdir("photos/2026/trip")))
shutil.rmtree("photos")                 # delete a whole folder tree: be careful!
print(os.path.exists("photos"))
