# 4.2 Scope and recursion: LEGB, closures and the call stack
# Example "unbound" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

count = 10

def broken():
    print(count)      # count is local here because of the line below
    count = 5

try:
    broken()
except UnboundLocalError as err:
    print("UnboundLocalError:", err)
