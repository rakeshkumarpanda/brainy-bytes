# 5.1 Exceptions: try, except, else, finally and raise
# Example "assert" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

def percent(part, whole):
    assert whole > 0, "whole must be positive"     # a check for programmers
    return 100 * part / whole

print(percent(3, 4))
try:
    percent(1, 0)
except AssertionError as err:
    print("AssertionError:", err)
# python -O turns every assert off, so never use assert to check user input
