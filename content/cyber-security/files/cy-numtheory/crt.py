# 2.1 Number theory for cryptography: modular arithmetic to primes
# Example "crt" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# The Chinese remainder theorem: rebuild x from its remainders
def crt(remainders, moduli):
    M = 1
    for m in moduli:
        M = M * m
    x = 0
    for a, m in zip(remainders, moduli):
        Mi = M // m
        yi = pow(Mi, -1, m)              # the inverse of Mi modulo m
        x = x + a * Mi * yi
    return x % M

print("Sun Zi's puzzle:", crt([2, 3, 2], [3, 5, 7]))

# RSA style: work modulo p and q separately, then join the answers
p, q = 61, 53
n = p * q
secret = 1234
mp, mq = secret % p, secret % q
print("1234 mod 61 =", mp, " 1234 mod 53 =", mq, " rebuilt:", crt([mp, mq], [p, q]))
