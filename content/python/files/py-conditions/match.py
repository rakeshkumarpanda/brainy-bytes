# 2.1 Making decisions: if, elif, else and match
# Example "match" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

def describe(command):
    match command.split():
        case ["quit"] | ["exit"]:
            return "Goodbye!"
        case ["go", direction] if direction in ("up", "down"):
            return "You climb " + direction
        case ["go", direction]:
            return "You walk " + direction
        case ["drop", *things]:
            return "You drop " + str(len(things)) + " thing(s)"
        case _:
            return "I do not understand"

for c in ["go north", "go up", "drop sword lamp", "quit", "dance"]:
    print(c.ljust(16), "->", describe(c))
