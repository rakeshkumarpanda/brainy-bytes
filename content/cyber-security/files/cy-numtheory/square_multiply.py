# 2.1 Number theory for cryptography: modular arithmetic to primes
# Example "square_multiply" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# b^e mod n by square and multiply, compared with Python's pow
def power_mod(b, e, n):
    result = 1
    steps = 0
    for bit in bin(e)[2:]:              # the bits of e from left to right
        result = result * result % n    # square for every bit
        steps = steps + 1
        if bit == "1":
            result = result * b % n     # multiply when the bit is 1
            steps = steps + 1
    return result, steps

value, steps = power_mod(4, 13, 497)
print("4^13 mod 497 =", value, "in", steps, "steps")

big_n = 2 ** 127 - 1                    # a Mersenne prime with 39 digits
value, steps = power_mod(123456789, 65537, big_n)
print("123456789^65537 mod (2^127 - 1) found in", steps, "steps")
print("same as pow():", value == pow(123456789, 65537, big_n))
