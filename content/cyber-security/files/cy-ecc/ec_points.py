# 2.4 Elliptic curve cryptography: ECDH, X25519, ECDSA and Ed25519
# Example "ec_points" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# The points of a small elliptic curve y^2 = x^3 + 2x + 2 over the field of 17 elements
p, a, b = 17, 2, 2
print("discriminant 4a^3 + 27b^2 mod p =", (4 * a ** 3 + 27 * b ** 2) % p, "(must not be 0)")

points = []
for x in range(p):
    right = (x ** 3 + a * x + b) % p
    for y in range(p):
        if (y * y) % p == right:
            points.append((x, y))
print("points:", points)
print("count with the point at infinity:", len(points) + 1)

# Hasse's theorem: |#E - (p + 1)| <= 2 sqrt(p)
count = len(points) + 1
print("Hasse bound:", p + 1, "+/-", round(2 * p ** 0.5, 2), "| holds:", abs(count - (p + 1)) <= 2 * p ** 0.5)

# Fast count with Euler's criterion: right side is a square when right^((p-1)/2) = 1
fast = 1                                   # the point at infinity
for x in range(p):
    right = (x ** 3 + a * x + b) % p
    if right == 0:
        fast = fast + 1
    elif pow(right, (p - 1) // 2, p) == 1:
        fast = fast + 2                    # y and -y
print("count by Euler's criterion:", fast)
