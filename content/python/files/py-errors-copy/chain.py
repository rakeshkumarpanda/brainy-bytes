# 1.4 Exceptions in depth, copying and serialisation
# Example "chain" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

def load_age(text):
    try:
        return int(text)
    except ValueError as err:
        raise RuntimeError("bad age in the form") from err     # explicit chaining


try:
    load_age("abc")
except RuntimeError as err:
    print("caught:", err)
    print("cause:", repr(err.__cause__))
    print("suppress context?", err.__suppress_context__)


try:
    try:
        {}["missing"]
    except KeyError:
        1 / 0                                  # an error while handling an error
except ZeroDivisionError as err:
    print("context:", repr(err.__context__))   # implicit chaining
    print("cause:", err.__cause__)


try:
    try:
        int("x")
    except ValueError:
        raise LookupError("not found") from None   # hide the original
except LookupError as err:
    print("from None:", err.__cause__, err.__suppress_context__)
