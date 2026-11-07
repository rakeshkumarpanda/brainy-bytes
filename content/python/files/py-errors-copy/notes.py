# 1.4 Exceptions in depth, copying and serialisation
# Example "notes" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

def parse_row(number, row):
    try:
        name, age = row.split(",")
        return name, int(age)
    except ValueError as err:
        err.add_note(f"while reading row {number}: {row!r}")   # Python 3.11+
        raise


try:
    for number, row in enumerate(["Asha,30", "Ravi,thirty"], start=1):
        print(parse_row(number, row))
except ValueError as err:
    print("ValueError:", err)
    print("notes:", err.__notes__)
