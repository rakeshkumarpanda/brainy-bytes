# 2.3 Diffie-Hellman, ElGamal and the discrete logarithm
# Example "elgamal" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# ElGamal encryption: Diffie-Hellman with a fresh random k for every message
import secrets

# Toy example from the worked problem
p, g = 23, 5
x = 6                                    # private key
h = pow(g, x, p)                         # public key h = g^x = 8
m, k = 10, 3                             # message and one time random k
c1 = pow(g, k, p)                        # 5^3 mod 23 = 10
c2 = m * pow(h, k, p) % p                # 10 * 8^3 mod 23 = 14
s = pow(c1, x, p)                        # shared value h^k = c1^x
print("ciphertext (c1, c2) =", (c1, c2), " decrypts to", c2 * pow(s, -1, p) % p)

# Larger toy group: safe prime p = 2q + 1, messages encoded as squares mod p
p = 1099511628443
q = (p - 1) // 2
g = 4
x = secrets.randbelow(q - 2) + 2
h = pow(g, x, p)

def encrypt(m):
    k = secrets.randbelow(q - 2) + 2     # NEW k for every message
    return pow(g, k, p), m * pow(h, k, p) % p

def decrypt(c1, c2):
    return c2 * pow(pow(c1, x, p), -1, p) % p

m = pow(4242, 2, p)                      # a square, so it lies in the subgroup
e1, e2 = encrypt(m), encrypt(m)
print("same message, different ciphertexts:", e1 != e2, "| both decrypt:", decrypt(*e1) == m == decrypt(*e2))

# Multiplying ciphertexts multiplies the messages (homomorphic, and also malleable)
m2 = pow(1000, 2, p)
f1, f2 = encrypt(m), encrypt(m2)
product = (f1[0] * f2[0] % p, f1[1] * f2[1] % p)
print("Dec(E(m) * E(m2)) = m * m2:", decrypt(*product) == m * m2 % p)

# Reusing k is fatal: one known message reveals every other one
k = secrets.randbelow(q - 2) + 2
known, secret_msg = pow(11, 2, p), pow(777, 2, p)
c_known = (pow(g, k, p), known * pow(h, k, p) % p)
c_secret = (pow(g, k, p), secret_msg * pow(h, k, p) % p)
mask = c_known[1] * pow(known, -1, p) % p          # h^k, worked out from the known pair
print("k reused, secret recovered:", c_secret[1] * pow(mask, -1, p) % p == secret_msg)
