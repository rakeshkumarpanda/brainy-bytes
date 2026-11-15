# 1.2 Post quantum cryptography: Shor, lattices, ML-KEM and ML-DSA
# Example "baby_kyber" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# A baby version of ML-KEM's core: Module-LWE with polynomials (toy sizes, NOT the real standard)
import random

rng = random.Random(7)
q, n, k = 3329, 8, 2                     # real ML-KEM: q = 3329, n = 256, k = 2, 3 or 4

def poly_mul(a, b):                      # multiply in Z_q[x] / (x^n + 1): x^n wraps round to -1
    out = [0] * n
    for i in range(n):
        for j in range(n):
            if i + j < n:
                out[i + j] = (out[i + j] + a[i] * b[j]) % q
            else:
                out[i + j - n] = (out[i + j - n] - a[i] * b[j]) % q
    return out

def poly_add(a, b):
    return [(x + y) % q for x, y in zip(a, b)]

def small():                             # coefficients from -2 to 2, like the CBD noise in ML-KEM
    return [rng.choice([-2, -1, 0, 1, 2]) % q for i in range(n)]

def mat_vec(M, v):                       # k by k matrix of polynomials times a vector of k polynomials
    out = []
    for row in M:
        acc = [0] * n
        for a, b in zip(row, v):
            acc = poly_add(acc, poly_mul(a, b))
        out.append(acc)
    return out

def transpose(M):
    return [[M[j][i] for j in range(k)] for i in range(k)]

# Key generation
A = [[[rng.randrange(q) for c in range(n)] for j in range(k)] for i in range(k)]
s = [small() for i in range(k)]
e = [small() for i in range(k)]
t = [poly_add(x, y) for x, y in zip(mat_vec(A, s), e)]        # public key (A, t), secret s

# Encrypt 8 message bits, each scaled to 0 or about q/2
message = [1, 0, 1, 1, 0, 1, 0, 0]
r = [small() for i in range(k)]
e1 = [small() for i in range(k)]
e2 = small()
u = [poly_add(x, y) for x, y in zip(mat_vec(transpose(A), r), e1)]
v = e2
for ti, ri in zip(t, r):
    v = poly_add(v, poly_mul(ti, ri))
v = poly_add(v, [bit * ((q + 1) // 2) for bit in message])

# Decrypt: v - s.u = m * q/2 + (small noise)
w = v
for si, ui in zip(s, u):
    w = [(x - y) % q for x, y in zip(w, poly_mul(si, ui))]
decoded = [1 if q // 4 < c < 3 * q // 4 else 0 for c in w]
print("message:", message)
print("decoded:", decoded, "| correct:", decoded == message)
print("noisy coefficients:", w)
print("public t here:", k * n, "numbers plus a seed for A. Real ML-KEM-768: k = 3, n = 256, 1184 bytes.")
