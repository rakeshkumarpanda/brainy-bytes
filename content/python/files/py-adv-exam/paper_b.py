# 8.1 Exam practice: PCPP1 style papers
# Example "paper_b" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

def gen():
    print("start")
    yield 1
    print("middle")
    yield 2


g = gen()
print("Q1 made")
print("Q1", next(g))
print("Q1", list(g))


def count(n):
    x = yield n
    print("got", x)
    yield x * 2


c = count(5)
print("Q2", next(c), c.send(10))


def inner():
    yield 1
    yield 2
    return "done"


def outer():
    result = yield from inner()
    yield result


print("Q3", list(outer()))

it = iter([1, 2, 3])
print("Q4", 2 in it, list(it))

import itertools

print("Q5", list(itertools.islice(itertools.count(10, 5), 3)), list(itertools.accumulate([1, 2, 3])))
print("Q6", list(itertools.chain("ab", [1])), [k for k, grp in itertools.groupby("aabbba")], len(list(itertools.combinations(range(5), 2))))

from contextlib import contextmanager


@contextmanager
def tag(name):
    print(f"<{name}>")
    try:
        yield name.upper()
    finally:
        print(f"</{name}>")


with tag("b") as t:
    print("Q7", t)


class Quiet:
    def __enter__(self):
        return self

    def __exit__(self, kind, value, tb):
        print("Q8 exit saw", kind.__name__)
        return True


with Quiet():
    1 / 0
print("Q8 after the with block")

try:
    try:
        {}["k"]
    except KeyError as err:
        raise ValueError("bad") from err
except ValueError as err:
    print("Q9", type(err.__cause__).__name__, err.__suppress_context__)

try:
    raise ExceptionGroup("many", [ValueError("a"), TypeError("b"), ValueError("c")])
except* ValueError as group:
    print("Q10 V", len(group.exceptions))
except* TypeError as group:
    print("Q10 T", len(group.exceptions))
