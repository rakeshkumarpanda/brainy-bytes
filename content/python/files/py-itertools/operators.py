# 2.2 itertools, functools and operator
# Example "operators" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

from operator import itemgetter, attrgetter, methodcaller
from dataclasses import dataclass

rows = [("Asha", 30, "Pune"), ("Ravi", 25, "Delhi"), ("Meera", 30, "Agra")]
print(sorted(rows, key=itemgetter(1, 0)))      # by age, then by name
name_and_city = itemgetter(0, 2)
print([name_and_city(r) for r in rows])


@dataclass
class Book:
    title: str
    pages: int


books = [Book("Python", 320), Book("Maths", 210)]
print([b.title for b in sorted(books, key=attrgetter("pages"))])
shout = methodcaller("upper")
print(list(map(shout, ["hi", "ok"])))
