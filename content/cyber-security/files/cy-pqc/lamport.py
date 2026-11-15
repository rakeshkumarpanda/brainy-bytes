# 1.2 Post quantum cryptography: Shor, lattices, ML-KEM and ML-DSA
# Example "lamport" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# Lamport one time signatures (1979): security from a hash function only, so quantum computers do not break it
import hashlib
import secrets

def H(data):
    return hashlib.sha256(data).digest()

def keygen():
    private = [[secrets.token_bytes(32), secrets.token_bytes(32)] for i in range(256)]
    public = [[H(a), H(b)] for a, b in private]
    return private, public

def bits_of(message):
    digest = int.from_bytes(H(message), "big")
    return [(digest >> (255 - i)) & 1 for i in range(256)]

def sign(private, message):
    return [private[i][bit] for i, bit in enumerate(bits_of(message))]   # reveal one secret per bit

def verify(public, message, signature):
    return all(H(signature[i]) == public[i][bit] for i, bit in enumerate(bits_of(message)))

private, public = keygen()
sig = sign(private, b"release v1.0")
print("signature size:", 256 * 32, "bytes, public key:", 2 * 256 * 32, "bytes")
print("valid:", verify(public, b"release v1.0", sig))
print("changed message valid:", verify(public, b"release v6.6", sig))

# Signing a second message with the same key reveals more secrets
sig2 = sign(private, b"release v2.0")
known = set()
for i in range(256):
    known.add((i, bits_of(b"release v1.0")[i]))
    known.add((i, bits_of(b"release v2.0")[i]))
both = sum(1 for i in range(256) if (i, 0) in known and (i, 1) in known)
print("after two signatures the attacker knows both secrets for", both, "of 256 positions")
print("so each key must sign ONE message. Merkle trees (XMSS, LMS) and SLH-DSA build many-time schemes from this idea.")
