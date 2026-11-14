# 1.2 Post quantum cryptography: Shor, lattices, ML-KEM and ML-DSA
# Example "lwe_toy" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# Learning With Errors: Regev's encryption of one bit at a time (toy sizes, not secure)
import random

rng = random.Random(42)
q, n, m = 97, 8, 20                      # modulus, secret length, number of public samples

s = [rng.randrange(q) for i in range(n)]                       # the secret vector
A = [[rng.randrange(q) for j in range(n)] for i in range(m)]  # public random matrix
e = [rng.choice([-1, 0, 1]) for i in range(m)]                 # small errors
b = [(sum(A[i][j] * s[j] for j in range(n)) + e[i]) % q for i in range(m)]
# public key: (A, b). Without the errors, Gaussian elimination would find s at once.

def encrypt(bit):
    rows = [i for i in range(m) if rng.random() < 0.5]        # a random subset of samples
    u = [sum(A[i][j] for i in rows) % q for j in range(n)]
    v = (sum(b[i] for i in rows) + bit * (q // 2)) % q
    return u, v

def decrypt(u, v):
    d = (v - sum(u[j] * s[j] for j in range(n))) % q           # = bit * q/2 + small noise
    return 0 if min(d, q - d) < q // 4 else 1, d

bits = [1, 0, 1, 1, 0, 0, 1, 0]
results = [decrypt(*encrypt(x)) for x in bits]
print("sent:     ", bits)
print("received: ", [r[0] for r in results])
print("noisy values (near 0 means 0, near 48 means 1):", [r[1] for r in results])

# Why the errors matter: without them, s falls out of plain linear algebra
print("with errors the public key looks random. With e = 0 it would be b = A s, solvable in milliseconds.")
