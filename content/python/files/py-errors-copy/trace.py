# 1.4 Exceptions in depth, copying and serialisation
# Example "trace" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

import traceback


def level3():
    return 10 / 0


def level2():
    return level3()


def level1():
    return level2()


try:
    level1()
except ZeroDivisionError as err:
    for frame in traceback.extract_tb(err.__traceback__):
        print(frame.name, "line", frame.lineno, ":", frame.line)
    print(traceback.format_exception_only(err)[-1].strip())
    print(type(err.__traceback__).__name__)
