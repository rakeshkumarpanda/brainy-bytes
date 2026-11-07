# 4.2 Scope and recursion: LEGB, closures and the call stack
# Example "legb" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

x = "global"

def outer():
    x = "enclosing"
    def inner():
        x = "local"
        print("inner sees:", x)
    inner()
    print("outer sees:", x)

outer()
print("module sees:", x)
print("len comes from:", len.__module__)   # the built-in scope
