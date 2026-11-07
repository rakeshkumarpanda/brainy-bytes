# 3.1 Clean code: PEP 8, docstrings and type hints
# Example "docstrings" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

import doctest


def average(numbers):
    """Return the mean of a non empty list of numbers.

    >>> average([2, 4, 6])
    4.0
    >>> average([5])
    5.0
    """
    return sum(numbers) / len(numbers)


class Wallet:
    """A simple wallet that holds money in rupees."""

    def __init__(self, amount=0):
        """Start with amount rupees (0 if not given)."""
        self.amount = amount


print(average.__doc__.splitlines()[0])
print(Wallet.__doc__, "|", Wallet.__init__.__doc__)
print(doctest.testmod())                       # runs the >>> examples above
