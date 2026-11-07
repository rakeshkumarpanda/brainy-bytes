# 2.1 Iterators and generators
# Example "iterclass" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

class Countdown:
    """An ITERATOR: it remembers where it is, so it can be used only once."""

    def __init__(self, start):
        self.current = start

    def __iter__(self):
        return self

    def __next__(self):
        if self.current <= 0:
            raise StopIteration
        value = self.current
        self.current -= 1
        return value


class Shelf:
    """An ITERABLE: every for loop gets a brand new iterator."""

    def __init__(self, books):
        self.books = books

    def __iter__(self):
        return iter(self.books)


c = Countdown(3)
print(list(c), list(c))                        # the second list is empty
s = Shelf(["Maths", "Python"])
print(list(s), list(s))                        # works every time
print(hasattr(c, "__next__"), hasattr(s, "__next__"))
