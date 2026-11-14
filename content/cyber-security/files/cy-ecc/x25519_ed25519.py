# 2.4 Elliptic curve cryptography: ECDH, X25519, ECDSA and Ed25519
# Example "x25519_ed25519" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# X25519 key exchange and Ed25519 signatures, checked against the RFC test vectors (pip install cryptography)
from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey, X25519PublicKey
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization
from cryptography.exceptions import InvalidSignature

raw = serialization.Encoding.Raw
pub_raw = serialization.PublicFormat.Raw

# RFC 7748, section 6.1
alice = X25519PrivateKey.from_private_bytes(bytes.fromhex("77076d0a7318a57d3c16c17251b26645df4c2f87ebc0992ab177fba51db92c2a"))
bob_public = X25519PublicKey.from_public_bytes(bytes.fromhex("de9edb7d7b7dc1b4d35b61c2ece435373f8343c85b78674dadfc7e146f882b4f"))
print("Alice's public key matches RFC 7748:",
      alice.public_key().public_bytes(raw, pub_raw).hex() == "8520f0098930a754748b7ddcb43ef75a0dbf3a0d26381af4eba4a98eaa9b4e6a")
shared = alice.exchange(bob_public)
print("shared secret matches RFC 7748:", shared.hex() == "4a5d9d5ba4ce2de1728e3bf480350f25e07e21c947d19e3376f09b3c1e161742")

# Fresh keys, the normal way
a, b = X25519PrivateKey.generate(), X25519PrivateKey.generate()
print("fresh X25519 exchange agrees:", a.exchange(b.public_key()) == b.exchange(a.public_key()), "| key size: 32 bytes")

# RFC 8032, Ed25519 test 1 (empty message)
signer = Ed25519PrivateKey.from_private_bytes(bytes.fromhex("9d61b19deffd5a60ba844af492ec2cc44449c5697b326919703bac031cae7f60"))
signature = signer.sign(b"")
print("Ed25519 signature matches RFC 8032:", signature.hex().startswith("e5564300c360ac72") and signature.hex().endswith("438e7a100b"))
print("signing twice gives the same signature (deterministic nonce):", signer.sign(b"") == signature)

key = Ed25519PrivateKey.generate()
sig = key.sign(b"firmware v3.1")
key.public_key().verify(sig, b"firmware v3.1")
print("verified,", len(sig), "byte signature")
try:
    key.public_key().verify(sig, b"firmware v3.2")
except InvalidSignature:
    print("changed firmware rejected")
