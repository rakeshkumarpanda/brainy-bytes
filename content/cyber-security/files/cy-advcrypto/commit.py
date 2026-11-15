# 1.3 Advanced cryptography: secret sharing, zero knowledge, homomorphic encryption and MPC
# Example "commit" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# Commitments: lock in a value now, reveal it later, and prove you did not change it
import hashlib
import secrets

def commit(value):
    salt = secrets.token_bytes(16)       # the salt hides small value sets (yes or no, 1 to 100)
    return hashlib.sha256(salt + value).hexdigest(), salt

def check(commitment, salt, value):
    return hashlib.sha256(salt + value).hexdigest() == commitment

c, salt = commit(b"my bid: 4200")
print("published commitment:", c[:24], "...")
print("honest reveal accepted:", check(c, salt, b"my bid: 4200"))
print("changed bid accepted:  ", check(c, salt, b"my bid: 3900"))

# Pedersen commitment: C = g^m * h^r mod p. Hiding for everyone, binding unless log_g(h) is known.
p = 1099511628443                        # toy safe prime from the Diffie-Hellman chapter
q = (p - 1) // 2
g, h = 4, 9                              # two generators of the order q subgroup, log_g(h) unknown to the committer
m1, r1 = 20, secrets.randbelow(q)
m2, r2 = 22, secrets.randbelow(q)
C1 = pow(g, m1, p) * pow(h, r1, p) % p
C2 = pow(g, m2, p) * pow(h, r2, p) % p
C_sum = C1 * C2 % p                      # commitments can be added without opening them
print("product of commitments opens to 42:", C_sum == pow(g, 42, p) * pow(h, (r1 + r2) % q, p) % p)
