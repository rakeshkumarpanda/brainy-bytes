# 1.3 Advanced cryptography: secret sharing, zero knowledge, homomorphic encryption and MPC
# Example "shamir" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# Shamir secret sharing (1979): any 3 of 5 shares rebuild the secret, 2 shares reveal nothing
import secrets

P = 2 ** 127 - 1                         # a prime. All arithmetic is mod P.

def split(secret, k, n):
    coeffs = [secret] + [secrets.randbelow(P) for i in range(k - 1)]   # f(0) = secret, degree k - 1
    shares = []
    for x in range(1, n + 1):
        y = 0
        for c in reversed(coeffs):       # Horner's rule for f(x)
            y = (y * x + c) % P
        shares.append((x, y))
    return shares

def rebuild(shares):                     # Lagrange interpolation at x = 0
    total = 0
    for i, (xi, yi) in enumerate(shares):
        num, den = 1, 1
        for j, (xj, yj) in enumerate(shares):
            if i != j:
                num = num * (-xj) % P
                den = den * (xi - xj) % P
        total = (total + yi * num * pow(den, -1, P)) % P
    return total

secret = int.from_bytes(b"vault code 7391", "big")
shares = split(secret, k=3, n=5)
print("5 shares made, any 3 rebuild the secret")
for pick in ([0, 1, 2], [1, 3, 4], [0, 2, 4]):
    got = rebuild([shares[i] for i in pick])
    print("shares", [shares[i][0] for i in pick], "->", got.to_bytes(15, "big"))
wrong = rebuild(shares[:2])
print("only 2 shares give a random looking number:", wrong == secret, "| value starts", str(wrong)[:12])
