# 2.4 Elliptic curve cryptography: ECDH, X25519, ECDSA and Ed25519
# Example "ec_compress" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# Point compression: store x and one bit for y, then rebuild y with a modular square root
p = 2 ** 256 - 2 ** 32 - 977               # secp256k1. p mod 4 = 3, so square roots are one power
G = (0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798,
     0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8)
print("p mod 4 =", p % 4)

def compress(P):
    x, y = P
    prefix = b"\x03" if y % 2 == 1 else b"\x02"      # 02 for even y, 03 for odd y
    return prefix + x.to_bytes(32, "big")

def decompress(data):
    x = int.from_bytes(data[1:], "big")
    right = (x ** 3 + 7) % p
    y = pow(right, (p + 1) // 4, p)        # a square root of right, because p = 3 mod 4
    if y * y % p != right:
        raise ValueError("x is not on the curve")
    if y % 2 != data[0] % 2:
        y = p - y                          # pick the root with the right parity
    return (x, y)

c = compress(G)
print("compressed G:", c.hex()[:20] + "...", len(c), "bytes instead of 65")
print("rebuilt correctly:", decompress(c) == G)
try:
    decompress(b"\x02" + (5).to_bytes(32, "big"))
except ValueError as error:
    print("x = 5:", error)
