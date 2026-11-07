# 2.1 Making decisions: if, elif, else and match
# Example "matchmore" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

def http_message(status):
    match status:
        case 200 | 201:
            return "OK"
        case 404:
            return "Not found"
        case int(code) if 500 <= code < 600:
            return "Server error " + str(code)
        case _:
            return "Something else"

def where(point):
    match point:
        case (0, 0):
            return "origin"
        case (0, y):
            return f"on the y axis at {y}"
        case (x, 0):
            return f"on the x axis at {x}"
        case {"x": x, "y": y}:
            return f"a dict point ({x}, {y})"
        case _:
            return "somewhere else"

print(http_message(201), "|", http_message(503), "|", http_message(302))
print(where((0, 0)), "|", where((0, 5)), "|", where((3, 0)), "|", where({"x": 1, "y": 2}))
