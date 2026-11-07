# 1.3 Class design: methods, properties, abstract classes and dataclasses
# Example "cached" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

from functools import cached_property


class Report:
    def __init__(self, numbers):
        self.numbers = numbers

    @cached_property                           # computed once, then stored on the object
    def total(self):
        print("adding up", len(self.numbers), "numbers")
        return sum(self.numbers)


r = Report(list(range(1, 101)))
print(r.total)
print(r.total)                                 # no second "adding up" line
print("total" in vars(r))                      # the answer now lives in the instance dict
del r.total                                    # forget it, the next read recomputes
print(r.total)
