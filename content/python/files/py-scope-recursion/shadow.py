# 4.2 Scope and recursion: LEGB, closures and the call stack
# Example "shadow" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

x = "global x"

def demo():
    x = "local x"     # a new local name that hides (shadows) the global one
    print("inside:", x)

demo()
print("outside:", x)  # the global was never touched

def no_list_change(items):
    items = [0, 0]    # rebinding the local name does not affect the caller
def list_change(items):
    items.append(99)  # changing the object does

nums = [1, 2]
no_list_change(nums)
list_change(nums)
print(nums)
