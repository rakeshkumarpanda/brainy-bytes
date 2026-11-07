# 5.3 Files: reading, writing, modes, paths and streams
# Example "streams" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

import sys

sys.stdout.write("stdout: normal output\n")      # print() writes here
print("errors belong on stderr", file=sys.stderr)  # shown in red in many terminals
print(sys.stdin.readable(), sys.stdout.writable())
print(type(sys.stdout).__name__)
