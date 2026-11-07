# 2.3 Context managers and the with statement
# Example "protocol" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

class Door:
    def __enter__(self):
        print("open")
        return "room"                          # this value goes into "as"

    def __exit__(self, kind, err, tb):
        print("close, got:", kind.__name__ if kind else None, err)
        return False                           # do not hide errors


with Door() as place:
    print("inside the", place)

try:
    with Door():
        print(1 / 0)
        print("never printed")
except ZeroDivisionError:
    print("the error still reached us")
