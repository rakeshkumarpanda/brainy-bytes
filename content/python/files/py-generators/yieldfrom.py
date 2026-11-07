# 2.1 Iterators and generators
# Example "yieldfrom" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

def flatten(items):
    for item in items:
        if isinstance(item, list):
            yield from flatten(item)           # hand over to a smaller generator
        else:
            yield item


print(list(flatten([1, [2, [3, 4]], [], 5])))


def worker():
    total = 0
    for n in [1, 2, 3]:
        yield n
        total += n
    return total                               # becomes StopIteration.value


def boss():
    result = yield from worker()               # yield from also gives back the return value
    print("worker returned", result)
    yield "boss done"


print(list(boss()))
