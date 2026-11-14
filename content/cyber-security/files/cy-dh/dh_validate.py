# 2.3 Diffie-Hellman, ElGamal and the discrete logarithm
# Example "dh_validate" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# Always check the other side's public value. Bad values force a guessable key.
p = 1099511628443                        # toy safe prime p = 2q + 1
q = (p - 1) // 2
g = 4
b = 314159265358                         # Bob's secret

def bob_key(A):
    return pow(A, b, p)

def valid(A):
    # 1 < A < p - 1, and A must lie in the subgroup of order q
    return 1 < A < p - 1 and pow(A, q, p) == 1

for A in (1, p - 1, 0, pow(g, 271828, p)):
    print("A =", A, "| Bob's key would be", bob_key(A), "| valid:", valid(A))
