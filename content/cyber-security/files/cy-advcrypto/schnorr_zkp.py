# 1.3 Advanced cryptography: secret sharing, zero knowledge, homomorphic encryption and MPC
# Example "schnorr_zkp" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# Schnorr's zero knowledge proof: prove you know x with y = g^x, without revealing x
import hashlib
import secrets

p = 1099511628443                        # toy safe prime p = 2q + 1 (41 bits). Real systems use 256 bit curves.
q = (p - 1) // 2
g = 4                                    # generator of the subgroup of prime order q

x = secrets.randbelow(q)                 # the prover's secret, for example a password derived key
y = pow(g, x, p)                         # public

def one_round(knows_x):
    if knows_x:
        r = secrets.randbelow(q)
        t = pow(g, r, p)                 # 1. commitment
        c = secrets.randbelow(q)         # 2. verifier's random challenge
        s = (r + c * x) % q              # 3. response
    else:                                # a cheater guesses the challenge in advance
        guess = secrets.randbelow(q)
        s = secrets.randbelow(q)
        t = pow(g, s, p) * pow(y, -guess, p) % p
        c = secrets.randbelow(q)         # the real challenge is almost never the guess
    return pow(g, s, p) == t * pow(y, c, p) % p          # check g^s = t * y^c

print("honest prover, 20 rounds accepted:", all(one_round(True) for i in range(20)))
print("cheater, 20 rounds accepted:      ", all(one_round(False) for i in range(20)))

# Fiat-Shamir: replace the verifier's challenge by a hash, giving a non interactive proof (a signature)
def prove(message):
    r = secrets.randbelow(q)
    t = pow(g, r, p)
    c = int.from_bytes(hashlib.sha256(f"{t},{y},{message}".encode()).digest(), "big") % q
    return t, (r + c * x) % q

def verify(message, t, s):
    c = int.from_bytes(hashlib.sha256(f"{t},{y},{message}".encode()).digest(), "big") % q
    return pow(g, s, p) == t * pow(y, c, p) % p

t, s = prove("login at 10:42")
print("non interactive proof valid:", verify("login at 10:42", t, s), "| reused for another message:", verify("login at 23:59", t, s))
