# 2.1 Iterators and generators
# Example "send" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

def running_average():
    total = 0
    count = 0
    average = None
    while True:
        value = yield average                  # send(v) puts v here
        total += value
        count += 1
        average = total / count


avg = running_average()
next(avg)                                      # "prime" it: run to the first yield
print(avg.send(10), avg.send(20), avg.send(60))


def guarded():
    try:
        while True:
            try:
                yield "working"
            except ValueError as err:
                print("handled inside:", err)
    finally:
        print("cleanup runs on close()")


g = guarded()
print(next(g))
print(g.throw(ValueError("bad value")))        # raise an error AT the paused yield
g.close()                                      # GeneratorExit inside, so finally runs
print(next(g, "closed"))
