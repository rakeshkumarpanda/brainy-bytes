# 1.2 Post quantum cryptography: Shor, lattices, ML-KEM and ML-DSA
# Example "pq_real" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# Real ML-KEM-768 and ML-DSA-65 (FIPS 203 and 204), plus a hybrid with X25519 (pip install cryptography)
from cryptography.hazmat.primitives.asymmetric import mlkem, mldsa
from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.exceptions import InvalidSignature

raw, pub_raw = serialization.Encoding.Raw, serialization.PublicFormat.Raw

# ML-KEM: a key encapsulation mechanism
receiver = mlkem.MLKEM768PrivateKey.generate()
public = receiver.public_key()
secret_sender, ciphertext = public.encapsulate()      # sender makes a random secret and wraps it
secret_receiver = receiver.decapsulate(ciphertext)     # receiver unwraps it
print("ML-KEM-768 public key:", len(public.public_bytes(raw, pub_raw)), "bytes, ciphertext:", len(ciphertext), "bytes")
print("shared secret:", len(secret_sender), "bytes, equal:", secret_sender == secret_receiver)

# Hybrid: secure if EITHER X25519 or ML-KEM holds (X25519MLKEM768 in TLS)
a, b = X25519PrivateKey.generate(), X25519PrivateKey.generate()
classical = a.exchange(b.public_key())
hybrid_key = HKDF(hashes.SHA256(), 32, None, b"hybrid demo").derive(secret_sender + classical)
print("hybrid key:", len(hybrid_key), "bytes from ML-KEM secret + X25519 secret")

# ML-DSA: lattice signatures
signer = mldsa.MLDSA65PrivateKey.generate()
signature = signer.sign(b"firmware 7.2")
verifier = signer.public_key()
verifier.verify(signature, b"firmware 7.2")
print("ML-DSA-65 public key:", len(verifier.public_bytes(raw, pub_raw)), "bytes, signature:", len(signature), "bytes, verified")
try:
    verifier.verify(signature, b"firmware 7.3")
except InvalidSignature:
    print("changed firmware rejected")
