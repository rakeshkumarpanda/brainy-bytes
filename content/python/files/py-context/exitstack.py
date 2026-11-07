# 2.3 Context managers and the with statement
# Example "exitstack" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

import os
import tempfile
from contextlib import ExitStack

folder = tempfile.mkdtemp()
names = ["a.txt", "b.txt", "c.txt"]            # how many files is only known at run time

with ExitStack() as stack:
    files = []
    for name in names:
        f = stack.enter_context(open(os.path.join(folder, name), "w"))
        files.append(f)
    stack.callback(print, "callback: every file is about to close")
    for number, f in enumerate(files, start=1):
        f.write("file " + str(number))
    print("open now:", sum(1 for f in files if not f.closed))
print("open after:", sum(1 for f in files if not f.closed))
