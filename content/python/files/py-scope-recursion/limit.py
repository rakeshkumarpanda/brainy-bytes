# 4.2 Scope and recursion: LEGB, closures and the call stack
# Example "limit" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

import sys
print("recursion limit:", sys.getrecursionlimit())

sys.setrecursionlimit(40)     # a small limit, only so this demo stays short

def forever(n):
    return forever(n + 1)     # no base case

try:
    forever(0)
except RecursionError as err:
    print("RecursionError:", err)

sys.setrecursionlimit(1000)   # put the normal limit back

def depth(n):
    return 0 if n == 0 else 1 + depth(n - 1)

print(depth(20))              # fine, well below the limit
