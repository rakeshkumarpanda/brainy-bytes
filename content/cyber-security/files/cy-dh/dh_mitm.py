# 2.3 Diffie-Hellman, ElGamal and the discrete logarithm
# Example "dh_mitm" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# Man in the middle on plain Diffie-Hellman, and a fingerprint check that exposes it
import hashlib
import secrets

p = 1099511628443                        # a toy safe prime (41 bits). Real systems use 2048 bits or more.
q = (p - 1) // 2
g = 4

def new_secret():
    return secrets.randbelow(q - 2) + 2

def fingerprint(key):                    # a short code people can compare by phone or in person
    return hashlib.sha256(str(key).encode()).hexdigest()[:8]

a, b, m = new_secret(), new_secret(), new_secret()
A, B, M = pow(g, a, p), pow(g, b, p), pow(g, m, p)

# Mallory replaces A and B with her own M
alice_key = pow(M, a, p)                 # Alice thinks this is shared with Bob
bob_key = pow(M, b, p)                   # Bob thinks this is shared with Alice
mallory_with_alice = pow(A, m, p)
mallory_with_bob = pow(B, m, p)

print("Mallory knows Alice's key:", mallory_with_alice == alice_key)
print("Mallory knows Bob's key:  ", mallory_with_bob == bob_key)
print("Alice and Bob share a key:", alice_key == bob_key)
print("fingerprints:", fingerprint(alice_key), "vs", fingerprint(bob_key), "-> attack exposed")

# Without Mallory the fingerprints match
honest_alice, honest_bob = pow(B, a, p), pow(A, b, p)
print("honest run fingerprints match:", fingerprint(honest_alice) == fingerprint(honest_bob))
