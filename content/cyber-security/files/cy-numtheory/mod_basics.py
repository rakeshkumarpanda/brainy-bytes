# 2.1 Number theory for cryptography: modular arithmetic to primes
# Example "mod_basics" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# Arithmetic modulo n: only the remainder matters
n = 7
print("17 mod 7 =", 17 % n)
print("-3 mod 7 =", -3 % n)                   # Python always gives 0 to n-1
print("(12 + 9) mod 7 =", (12 + 9) % n, "=", (12 % n + 9 % n) % n)
print("(12 x 9) mod 7 =", (12 * 9) % n, "=", (12 % n) * (9 % n) % n)

# Powers of 3 modulo 7 run through every non zero remainder: 3 is a generator
row = []
for k in range(1, 7):
    row.append(pow(3, k, n))
print("3^1 .. 3^6 mod 7:", row)

# Powers of 2 modulo 7 only reach three values
row = []
for k in range(1, 7):
    row.append(pow(2, k, n))
print("2^1 .. 2^6 mod 7:", row)
