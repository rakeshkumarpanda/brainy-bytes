# 4.2 Scope and recursion: LEGB, closures and the call stack
# Example "globalkw" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

visits = 0

def visit():
    global visits         # use the module level name, do not make a local one
    visits += 1

visit()
visit()
print("visits:", visits)

# Better: pass values in and return the new value
def next_count(count):
    return count + 1

total = 0
total = next_count(total)
total = next_count(total)
print("total:", total)
