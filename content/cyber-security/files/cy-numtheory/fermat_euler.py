# 2.1 Number theory for cryptography: modular arithmetic to primes
# Example "fermat_euler" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# Fermat's little theorem and Euler's theorem, checked by computer
from math import gcd

p = 101
ok = True
for a in range(1, p):
    if pow(a, p - 1, p) != 1:
        ok = False
print("a^100 mod 101 = 1 for every a from 1 to 100:", ok)

def phi_count(n):                       # count numbers below n that share no factor with n
    count = 0
    for k in range(1, n):
        if gcd(k, n) == 1:
            count = count + 1
    return count

def phi_formula(p, q):                  # for n = p * q with two different primes
    return (p - 1) * (q - 1)

print("phi(36) =", phi_count(36))
print("phi(143) by counting =", phi_count(143), " by formula =", phi_formula(11, 13))

n = 143
print("Euler: 7^phi(143) mod 143 =", pow(7, phi_formula(11, 13), n))
print("so 7^1000 mod 143 = 7^(1000 mod 120) mod 143 =", pow(7, 1000 % 120, n), "=", pow(7, 1000, n))
