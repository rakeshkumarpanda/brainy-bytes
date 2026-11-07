# 2.3 Context managers and the with statement
# Example "many" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

class Named:
    def __init__(self, name):
        self.name = name

    def __enter__(self):
        print("enter", self.name)
        return self.name

    def __exit__(self, kind, err, tb):
        print("exit", self.name)
        return False


with Named("A") as a, Named("B") as b:
    print("body with", a, b)

with (
    Named("outer") as x,
    Named("inner") as y,                       # the bracket form (Python 3.10 and later)
):
    print("body with", x, y)
