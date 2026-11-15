# 2.1 Number theory for cryptography: modular arithmetic to primes
# Example "primes" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# Primality testing: Fermat's test is fooled by Carmichael numbers, Miller-Rabin is not
import secrets

def fermat_test(n, a):
    return pow(a, n - 1, n) == 1

def miller_rabin(n, rounds=20):
    if n < 4:
        return n in (2, 3)
    if n % 2 == 0:
        return False
    d, s = n - 1, 0
    while d % 2 == 0:                    # write n - 1 = 2^s * d with d odd
        d, s = d // 2, s + 1
    for i in range(rounds):
        a = secrets.randbelow(n - 3) + 2
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        for j in range(s - 1):
            x = x * x % n
            if x == n - 1:
                break
        else:
            return False                 # a is a witness: n is surely composite
    return True                          # probably prime, error at most 4^-rounds

print("561 = 3 x 11 x 17 passes Fermat with a = 2:", fermat_test(561, 2))
print("Miller-Rabin says 561 is prime:", miller_rabin(561))
print("Miller-Rabin says 2^127 - 1 is prime:", miller_rabin(2 ** 127 - 1))

# Make a random 256 bit prime the way key generators do
tries = 0
while True:
    candidate = secrets.randbits(256) | (1 << 255) | 1   # top bit set (full size) and odd
    tries = tries + 1
    if miller_rabin(candidate):
        break
print("found a 256 bit prime after", tries, "odd candidates (about 89 expected)")
