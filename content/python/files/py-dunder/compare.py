# 1.1 Special methods and operator overloading
# Example "compare" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

from functools import total_ordering


@total_ordering                                # writes <=, > and >= from == and <
class Version:
    def __init__(self, text):
        self.parts = tuple(int(p) for p in text.split("."))

    def __repr__(self):
        return "Version(" + ".".join(str(p) for p in self.parts) + ")"

    def __eq__(self, other):
        return self.parts == other.parts

    def __lt__(self, other):
        return self.parts < other.parts        # tuples compare item by item


versions = [Version("3.14.0"), Version("3.9.7"), Version("3.10.2")]
print(sorted(versions))
print(max(versions), Version("3.9") <= Version("3.10"), Version("2.7") >= Version("3.0"))
print(sorted(["3.14.0", "3.9.7", "3.10.2"]))   # as plain text the order is wrong
