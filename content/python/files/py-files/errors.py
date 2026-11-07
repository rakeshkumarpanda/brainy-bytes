# 5.3 Files: reading, writing, modes, paths and streams
# Example "errors" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

import errno, os

try:
    open("no_such_file.txt")
except FileNotFoundError as err:
    print(type(err).__name__, err.errno, err.strerror, err.filename)
    print(err.errno == errno.ENOENT, isinstance(err, OSError))

try:
    open("no_such_file.txt")
except OSError as err:                     # the parent of every file error
    if err.errno == errno.ENOENT:
        print("not found:", os.strerror(err.errno))
    elif err.errno == errno.EACCES:
        print("no permission")
