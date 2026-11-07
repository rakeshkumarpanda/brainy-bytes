# 2.2 Loops: while, for, range, break and continue
# Example "digits" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

# Taking a number apart digit by digit with % and //
n = 90731
digits = []
while n > 0:
    digits.append(n % 10)   # the last digit
    n = n // 10             # drop the last digit
print(digits)               # in reverse order
print("sum of digits:", sum(digits))

# Collatz: halve if even, else 3n + 1, until 1. Nobody has proved it always ends!
n, steps = 27, 0
while n != 1:
    n = n // 2 if n % 2 == 0 else 3 * n + 1
    steps += 1
print("27 reaches 1 after", steps, "steps")
