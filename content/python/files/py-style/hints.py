# 3.1 Clean code: PEP 8, docstrings and type hints
# Example "hints" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

def greet(name: str, times: int = 1) -> str:
    return ("Hello " + name + "! ") * times


def first[T](items: list[T]) -> T:             # a generic function (Python 3.12 and later)
    return items[0]


scores: dict[str, int] = {"asha": 90}
maybe: int | None = None

print(greet("Asha", 2))
print(first([3, 1, 2]), first(["x", "y"]))
print(greet.__annotations__)
print(first("hello"))                          # a str, not a list: Python does not check hints
