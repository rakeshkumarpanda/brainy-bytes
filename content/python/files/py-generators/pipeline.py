# 2.1 Iterators and generators
# Example "pipeline" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

from itertools import islice

LOG = [
    "INFO start",
    "ERROR disk full",
    "INFO saved",
    "ERROR timeout",
    "WARN slow",
    "ERROR disk full",
]


def read_lines(lines):
    for line in lines:
        print("  read:", line)
        yield line


def only_errors(lines):
    for line in lines:
        if line.startswith("ERROR"):
            yield line


def message(lines):
    for line in lines:
        yield line.split(" ", 1)[1]


steps = message(only_errors(read_lines(LOG)))  # nothing is read yet
print("pipeline built")
print(list(islice(steps, 2)))                  # stop after 2 errors
