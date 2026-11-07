# 3.1 Clean code: PEP 8, docstrings and type hints
# Example "typing" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

from dataclasses import dataclass
from typing import Callable, Final, Literal, Protocol, TypedDict

MAX_USERS: Final = 100                         # checkers forbid changing a Final name


class Point(TypedDict):                        # the shape of a dict
    x: int
    y: int


type Direction = Literal["up", "down"]         # only these two strings (alias syntax: 3.12+)


def move(p: Point, way: Direction) -> Point:
    step = 1 if way == "up" else -1
    return {"x": p["x"], "y": p["y"] + step}


class Speaker(Protocol):                       # any class with a speak() method fits
    def speak(self) -> str: ...


@dataclass
class Dog:
    name: str

    def speak(self) -> str:
        return self.name + " says woof"


def introduce(s: Speaker) -> str:
    return "Meet: " + s.speak()


def apply(f: Callable[[int], int], value: int) -> int:
    return f(value)


print(move({"x": 0, "y": 0}, "up"))
print(introduce(Dog("Rex")), apply(abs, -7), MAX_USERS)
